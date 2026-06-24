import configparser
import os
import tempfile
from pathlib import Path

import pytest

from src.models.profile import Profile
from src.patches.android_patches import (
    _extract_indent,
    _patch_application_back,
    _patch_activity_theme_impl,
    patch_back_functionality,
    patch_activity_theme,
)


class TestExtractIndent:
    def test_extracts_indent(self):
        tag = '\n    <application\n    android:label="test">'
        indent = _extract_indent(tag)
        assert indent == "    "

    def test_empty_fallback(self):
        tag = "<application>"
        indent = _extract_indent(tag)
        assert indent == "                 "


class TestPatchApplicationBack:
    def test_adds_attribute_when_missing(self):
        content = '<application android:label="test">\n</application>'
        result = _patch_application_back(content, None)
        assert result is not None
        assert 'android:enableOnBackInvokedCallback="false"' in result
        assert result != content

    def test_changes_true_to_false(self):
        content = '<application android:enableOnBackInvokedCallback="true">\n</application>'
        result = _patch_application_back(content, None)
        assert result is not None
        assert 'android:enableOnBackInvokedCallback="false"' in result
        assert 'android:enableOnBackInvokedCallback="true"' not in result

    def test_skips_when_already_false(self):
        content = '<application android:enableOnBackInvokedCallback="false">\n</application>'
        result = _patch_application_back(content, None)
        assert result is None

    def test_no_application_tag_returns_none(self):
        content = "<activity></activity>"
        result = _patch_application_back(content, None)
        assert result is None

    def test_modifies_only_first_application_tag(self):
        content = (
            '<application android:enableOnBackInvokedCallback="true">\n</application>\n'
            '<application android:enableOnBackInvokedCallback="true">\n</application>'
        )
        result = _patch_application_back(content, None)
        assert result is not None
        assert result.count('android:enableOnBackInvokedCallback="false"') == 1
        assert result.count('android:enableOnBackInvokedCallback="true"') == 1


class TestPatchActivityThemeImpl:
    def test_changes_theme_when_different(self):
        content = (
            '<activity android:name="{{args.android_entrypoint}}"'
            ' android:theme="@style/AppTheme">\n</activity>'
        )
        result = _patch_activity_theme_impl(content, None)
        assert result is not None
        assert 'android:theme="@style/AppTheme.NoEdgeToEdge"' in result

    def test_skips_when_already_correct(self):
        content = (
            '<activity android:name="{{args.android_entrypoint}}"'
            ' android:theme="@style/AppTheme.NoEdgeToEdge">\n</activity>'
        )
        result = _patch_activity_theme_impl(content, None)
        assert result is None

    def test_adds_theme_when_missing(self):
        content = '<activity android:name="{{args.android_entrypoint}}">\n</activity>'
        result = _patch_activity_theme_impl(content, None)
        assert result is not None
        assert 'android:theme="@style/AppTheme.NoEdgeToEdge"' in result

    def test_no_matching_activity_returns_none(self):
        content = '<activity android:name="com.example.OtherActivity">\n</activity>'
        result = _patch_activity_theme_impl(content, None)
        assert result is None

    def test_patches_only_target_activity(self):
        content = (
            '<activity android:name="com.example.Other">\n</activity>\n'
            '<activity android:name="{{args.android_entrypoint}}"'
            ' android:theme="@style/AppTheme">\n</activity>'
        )
        result = _patch_activity_theme_impl(content, None)
        assert result is not None
        assert result.count('@style/AppTheme.NoEdgeToEdge') == 1


class TestPatchBackFunctionality:
    def test_missing_buildozer_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Profile(name="test", wsl_dir=tmp, sourcedir=tmp)
            result = patch_back_functionality(Path(tmp), profile=p, log_callback=None)
            assert result is True

    def test_no_template_paths_without_spec(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Profile(name="test", wsl_dir=tmp, sourcedir=tmp)
            result = patch_back_functionality(Path(tmp), profile=p, log_callback=None)
            assert result is True

    def test_accepts_kwargs(self):
        result = patch_back_functionality(Path("."), profile=None, log_callback=None)
        assert result is True


class TestPatchActivityTheme:
    def test_missing_buildozer_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Profile(name="test", wsl_dir=tmp, sourcedir=tmp)
            result = patch_activity_theme(Path(tmp), profile=p, log_callback=None)
            assert result is True

    def test_no_template_paths_without_spec(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Profile(name="test", wsl_dir=tmp, sourcedir=tmp)
            result = patch_activity_theme(Path(tmp), profile=p, log_callback=None)
            assert result is True

    def test_accepts_kwargs(self):
        result = patch_activity_theme(Path("."), profile=None, log_callback=None)
        assert result is True
