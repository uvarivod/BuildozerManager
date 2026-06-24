import configparser
import os
import re
from pathlib import Path

from src.patches import register_patch


def _get_template_paths(buildozer_path: Path, profile=None) -> list[str]:
    spec_paths = []
    if profile:
        if profile.spec_path and os.path.exists(profile.spec_path):
            spec_paths.append(profile.spec_path)
        elif profile.sourcedir:
            candidate = os.path.join(profile.sourcedir, "buildozer.spec")
            if os.path.exists(candidate):
                spec_paths.append(candidate)
    wsl_spec = os.path.join(str(buildozer_path.parent), "buildozer.spec")
    if os.path.exists(wsl_spec):
        spec_paths.append(wsl_spec)

    archs_joined = None
    package_name = None
    for sp in spec_paths:
        config = configparser.ConfigParser()
        config.read(sp)
        try:
            archs = config.get("app", "android.archs")
            archs_joined = "_".join(a.strip() for a in archs.split(","))
            package_name = config.get("app", "package.name")
            break
        except Exception:
            continue

    if not archs_joined or not package_name:
        return []

    wsldir = str(buildozer_path.parent)
    return [
        f"{wsldir}/.buildozer/android/platform/python-for-android/pythonforandroid/bootstraps/_sdl_common/build/templates/AndroidManifest.tmpl.xml",
        f"{wsldir}/.buildozer/android/platform/build-{archs_joined}/build/bootstrap_builds/sdl2/templates/AndroidManifest.tmpl.xml",
        f"{wsldir}/.buildozer/android/platform/build-{archs_joined}/dists/{package_name}/templates/AndroidManifest.tmpl.xml",
    ]


def _get_archs_and_package(buildozer_path: Path, profile=None):
    spec_paths = []
    if profile:
        if profile.spec_path and os.path.exists(profile.spec_path):
            spec_paths.append(profile.spec_path)
        elif profile.sourcedir:
            candidate = os.path.join(profile.sourcedir, "buildozer.spec")
            if os.path.exists(candidate):
                spec_paths.append(candidate)
    wsl_spec = os.path.join(str(buildozer_path.parent), "buildozer.spec")
    if os.path.exists(wsl_spec):
        spec_paths.append(wsl_spec)

    for sp in spec_paths:
        config = configparser.ConfigParser()
        config.read(sp)
        try:
            archs = config.get("app", "android.archs")
            archs_joined = "_".join(a.strip() for a in archs.split(","))
            package_name = config.get("app", "package.name")
            return archs_joined, package_name
        except Exception:
            continue
    return None, None


def _extract_indent(tag):
    indent_match = re.findall(r"\n([ \t]+)[a-zA-Z{]", tag)
    return indent_match[-1] if indent_match else "                 "


def _log(log_cb, level, msg, log_too=None):
    if log_cb:
        log_cb(level, msg)
    if log_too is not None:
        log_too(level, msg)


def _patch_manifest_file(filepath, patch_func, log_cb):
    if not os.path.exists(filepath):
        if log_cb:
            log_cb("warn", f"Search file at path [{filepath}] -> [FAILED] (File not found)")
        return True
    if log_cb:
        log_cb("info", f"Search file at path [{filepath}] -> [SUCCESS]")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        if log_cb:
            log_cb("error", f"Read file content -> [FAILED] ({str(e)})")
        return False

    new_content = patch_func(content, log_cb)
    if new_content is None:
        return True

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        if log_cb:
            log_cb("success", f"Save modified file -> [SUCCESS]")
        return True
    except Exception as e:
        if log_cb:
            log_cb("error", f"Save modified file -> [FAILED] ({str(e)})")
        return False


def _patch_application_back(content, log_cb):
    app_tags = re.findall(r"(<application\b[^>]*>)", content, flags=re.DOTALL)
    total_found = len(app_tags)
    if log_cb:
        log_cb("info", f"Total <application> tags found: {total_found}")
    if total_found == 0:
        if log_cb:
            log_cb("error", "No <application> tags found in file")
        return None

    param_pattern = r'android:enableOnBackInvokedCallback=[\"\'](true|false)[\"\']'
    target_param = 'android:enableOnBackInvokedCallback="false"'

    first_tag_match = None
    for i, tag in enumerate(app_tags, start=1):
        match = re.search(param_pattern, tag)
        current_value = match.group(1) if match else "NOT FOUND"
        if log_cb:
            log_cb("info", f"Tag #{i} current value: {current_value}")
        if i == 1:
            first_tag_match = match

    original_first_tag = app_tags[0]
    has_changes = False

    if first_tag_match:
        if log_cb:
            log_cb("info", "Search parameter <android:enableOnBackInvokedCallback> in Tag #1 -> [FOUND]")
        if first_tag_match.group(1) == "false":
            if log_cb:
                log_cb("success", "Already set to 'false', no change needed")
            return None
        if log_cb:
            log_cb("info", "Value is 'true', modifying to 'false'")
        modified_first_tag = re.sub(param_pattern, target_param, original_first_tag)
        has_changes = True
    else:
        if log_cb:
            log_cb("info", "Parameter not found, inserting into Tag #1")
        indent = _extract_indent(original_first_tag)
        replacement = f"\n{indent}{target_param}>"
        modified_first_tag = original_first_tag.rstrip().rstrip(">") + replacement
        has_changes = True

    if not has_changes:
        return None

    return content.replace(original_first_tag, modified_first_tag, 1)


def _patch_activity_theme_impl(content, log_cb):
    activity_pattern = r'(<activity\b.*?(?<!%)(?<!\d)>)(?=\s*(?:<!--|<intent-filter|</activity>))'
    activity_tags = re.findall(activity_pattern, content, flags=re.DOTALL)
    total_found = len(activity_tags)

    if total_found == 0:
        activity_pattern = r"(<activity\b.*?>)\s*\n"
        activity_tags = re.findall(activity_pattern, content, flags=re.DOTALL)
        total_found = len(activity_tags)
        if total_found == 0:
            if log_cb:
                log_cb("error", "No valid <activity> tags matched template")
            return None

    target_activity_name = 'android:name="{{args.android_entrypoint}}"'
    theme_pattern = r'android:theme=[\"\']([^\"\']+)[\"\']'
    target_theme = 'android:theme="@style/AppTheme.NoEdgeToEdge"'

    target_tag_index = -1
    original_target_tag = None
    first_theme_match = None

    for i, tag in enumerate(activity_tags, start=1):
        is_target = target_activity_name in tag or "android:name='{{args.android_entrypoint}}'" in tag
        theme_match = re.search(theme_pattern, tag)
        current_theme = theme_match.group(1) if theme_match else "NOT FOUND"
        status_suffix = " [TARGET]" if is_target else ""
        if log_cb:
            log_cb("info", f"Activity #{i} current theme: {current_theme}{status_suffix}")
        if is_target and target_tag_index == -1:
            target_tag_index = i
            original_target_tag = tag
            first_theme_match = theme_match

    if target_tag_index == -1:
        if log_cb:
            log_cb("error", f"Target <activity> with name '{target_activity_name}' not found")
        return None

    if log_cb:
        log_cb("info", f"Target activity found at position #{target_tag_index}")

    has_changes = False

    if first_theme_match:
        if log_cb:
            log_cb("info", f"Search parameter <android:theme> -> [FOUND]")
        if first_theme_match.group(1) == "@style/AppTheme.NoEdgeToEdge":
            if log_cb:
                log_cb("success", "Already correct, no change needed")
            return None
        if log_cb:
            log_cb("info", f"Modifying theme from '{first_theme_match.group(1)}'")
        modified_target_tag = re.sub(theme_pattern, target_theme, original_target_tag)
        has_changes = True
    else:
        if log_cb:
            log_cb("info", "Search parameter <android:theme> -> [NOT FOUND], inserting")
        indent = _extract_indent(original_target_tag)
        stripped_tag = original_target_tag.rstrip()
        base_tag = re.sub(r">$", "", stripped_tag)
        replacement = f"\n{indent}{target_theme}\n{indent}>"
        modified_target_tag = base_tag.rstrip() + replacement
        has_changes = True

    if not has_changes:
        return None

    return content.replace(original_target_tag, modified_target_tag, 1)


def _check_theme_style_exists(buildozer_path: Path, profile, log_cb):
    archs_joined, package_name = _get_archs_and_package(buildozer_path, profile)
    if not archs_joined or not package_name:
        if log_cb:
            log_cb("error", "Could not determine archs/package from buildozer.spec, skipping themes.xml check")
        return True

    wsldir = str(buildozer_path.parent)
    values_dir = f"{wsldir}/.buildozer/android/platform/build-{archs_joined}/dists/{package_name}/src/main/res/values"

    if not os.path.isdir(values_dir):
        if log_cb:
            log_cb("error", f"Resource values directory not found at {values_dir}")
            log_cb("info", "\nInstructions to prepare your app for EdgeToEdge patching:")
            log_cb("info", "1. Create folder 'android_res/values' in your project root directory")
            log_cb("info", "2. Create file 'android_res/values/themes.xml' with this content:")
            log_cb("info", '   <resources>')
            log_cb("info", '       <style name="AppTheme.NoEdgeToEdge" parent="android:Theme.NoTitleBar.Fullscreen">')
            log_cb("info", '           <item name="android:windowTranslucentStatus">false</item>')
            log_cb("info", '           <item name="android:windowTranslucentNavigation">false</item>')
            log_cb("info", '           <item name="android:fitsSystemWindows">true</item>')
            log_cb("info", '       </style>')
            log_cb("info", '   </resources>')
            log_cb("info", "3. Add or update this line in your buildozer.spec:")
            log_cb("info", "   android.add_resources = android_res")
            log_cb("info", "4. Rebuild your app so buildozer copies the theme resource")
            log_cb("info", "5. Run this patch again after the build completes\n")
        return False

    style_found = False
    try:
        for entry in os.listdir(values_dir):
            if entry.endswith(".xml"):
                filepath = os.path.join(values_dir, entry)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if "AppTheme.NoEdgeToEdge" in content:
                    style_found = True
                    if log_cb:
                        log_cb("success", f"Found 'AppTheme.NoEdgeToEdge' style in {filepath}")
                    break
    except Exception as e:
        if log_cb:
            log_cb("error", f"Failed to scan resource files: {e}")
        return False

    if not style_found:
        if log_cb:
            log_cb("error", "'AppTheme.NoEdgeToEdge' style not found in any resource XML file")
            log_cb("info", "\nInstructions to prepare your app for EdgeToEdge patching:")
            log_cb("info", "1. Create folder 'android_res/values' in your project root directory")
            log_cb("info", "2. Create file 'android_res/values/themes.xml' with this content:")
            log_cb("info", '   <resources>')
            log_cb("info", '       <style name="AppTheme.NoEdgeToEdge" parent="android:Theme.NoTitleBar.Fullscreen">')
            log_cb("info", '           <item name="android:windowTranslucentStatus">false</item>')
            log_cb("info", '           <item name="android:windowTranslucentNavigation">false</item>')
            log_cb("info", '           <item name="android:fitsSystemWindows">true</item>')
            log_cb("info", '       </style>')
            log_cb("info", '   </resources>')
            log_cb("info", "3. Add or update this line in your buildozer.spec:")
            log_cb("info", "   android.add_resources = android_res")
            log_cb("info", "4. Rebuild your app so buildozer copies the theme resource")
            log_cb("info", "5. Run this patch again after the build completes\n")
        return False

    return True


def _apply_to_templates(buildozer_path, profile, content_patch_func, log_cb):
    templates = _get_template_paths(buildozer_path, profile)

    if not templates:
        if log_cb:
            log_cb("warn", "Could not resolve template paths (buildozer.spec may be missing or unreadable)")
        return True

    all_ok = True
    for filepath in templates:
        if log_cb:
            log_cb("info", f"\nPatching: {filepath}")
        ok = _patch_manifest_file(filepath, content_patch_func, log_cb)
        if not ok:
            all_ok = False
    return all_ok


@register_patch(name="patch_back_functionality", description="Restores Android Back button for Android 16+")
def patch_back_functionality(buildozer_path: Path, **kwargs):
    profile = kwargs.get("profile")
    log_cb = kwargs.get("log_callback")
    return _apply_to_templates(buildozer_path, profile, _patch_application_back, log_cb)


@register_patch(name="patch_activity_theme", description="Disables EdgeToEdge display mode in Android app")
def patch_activity_theme(buildozer_path: Path, **kwargs):
    profile = kwargs.get("profile")
    log_cb = kwargs.get("log_callback")

    themes_ok = _check_theme_style_exists(buildozer_path, profile, log_cb)
    if not themes_ok:
        if log_cb:
            log_cb("error", "AppTheme.NoEdgeToEdge style not found, aborting activity theme patching")
        return False

    return _apply_to_templates(buildozer_path, profile, _patch_activity_theme_impl, log_cb)
