#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

import os
import atexit

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)

from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'device/oneplus/sm8450-common',
    'hardware/oplus',
    'hardware/qcom-caf/sm8450',
    'hardware/qcom-caf/wlan',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/commonsys/display',
    'vendor/qcom/opensource/dataservices',
]

def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_vendor' if partition in ['odm', 'vendor'] else None


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'com.qualcomm.qti.dpm.api@1.0',
        'libmmosal',
        'libvibrator',
        'vendor.qti.diaghal@1.0',
        'vendor.qti.hardware.dpmservice@1.0',
        'vendor.qti.hardware.dpmservice@1.1',
        'vendor.qti.hardware.qccsyshal@1.0',
        'vendor.qti.hardware.qccsyshal@1.1',
        'vendor.qti.hardware.qccvndhal@1.0',
        'vendor.qti.hardware.wifidisplaysession@1.0',
        'vendor.qti.imsrtpservice@3.0',
    ): lib_fixup_vendor_suffix,
}

blob_fixups: blob_fixups_user_type = {
    'vendor/lib64/libsnapdragoncolor-manager.so': blob_fixup()
        .replace_needed('libtinyxml2.so', 'libtinyxml2_1.so'),
    'vendor/bin/hw/vendor.qti.hardware.display.composer-service': blob_fixup()
        .replace_needed('vendor.qti.hardware.display.config-V5-ndk_platform.so', 'vendor.qti.hardware.display.config-V5-ndk.so')
        .replace_needed('android.hardware.common-V2-ndk_platform.so', 'android.hardware.common-V2-ndk.so'),
    'odm/bin/hw/vendor.oplus.hardware.charger-V10-service': blob_fixup()
        .add_needed('libbase_shim.so')
        .replace_needed('vendor.oplus.hardware.osense.client-V1-ndk_platform.so', 'vendor.oplus.hardware.osense.client-V1-ndk.so'),
    'odm/bin/hw/vendor-oplus-hardware-performance-V1-service': blob_fixup()
        .add_needed('libbase_shim.so')
        .add_needed('libprocessgroup_shim.so'),
    'odm/etc/gps.conf': blob_fixup()
        .regex_replace('com.oplus.locationproxy', 'com.google.android.carrierlocation'),
    ('odm/lib64/mediadrm/libwvdrmengine.so', 'odm/lib64/libwvhidl.so'): blob_fixup()
        .add_needed('libcrypto_shim.so'),
    'odm/lib64/libosenseaidlhalclient.so': blob_fixup()
        .replace_needed('vendor.oplus.hardware.osense.client-V1-ndk_platform.so', 'vendor.oplus.hardware.osense.client-V1-ndk.so'),
    'product/app/PowerOffAlarm/PowerOffAlarm.apk': blob_fixup()
        .apktool_patch('blob-patches/PowerOffAlarm.patch'),
    'product/etc/sysconfig/com.android.hotwordenrollment.common.util.xml': blob_fixup()
        .regex_replace('/my_product', '/product'),
    ('system_ext/bin/horae', 'system_ext/lib64/vendor.qti.hardware.qccsyshal@1.2-halimpl.so'): blob_fixup()
        .replace_needed('libprotobuf-cpp-full.so', 'libprotobuf-cpp-full-21.7.so')
        .replace_needed('libprotobuf-cpp-lite.so', 'libprotobuf-cpp-lite-21.7.so'),
    'system_ext/lib64/libwfdnative.so': blob_fixup()
        .add_needed('libinput_shim.so')
        .add_needed('libbinder_shim.so'),
    'system_ext/lib64/libwfdmmsrc_system.so': blob_fixup()
        .add_needed('libgui_shim.so')
        .replace_needed('android.hidl.base@1.0.so', 'libhidlbase.so'),
    'system_ext/bin/wfdservice64': blob_fixup()
        .add_needed('libwfdservice_shim.so'),
    'system_ext/lib64/libwfdservice.so': blob_fixup()
        .replace_needed('android.media.audio.common.types-V2-cpp.so', 'android.media.audio.common.types-V4-cpp.so'),
    'vendor/bin/qguard': blob_fixup()
        .add_needed('libbase_shim.so'),
    ('vendor/etc/media_cape/video_system_specs.json', 'vendor/etc/media_taro/video_system_specs.json'): blob_fixup()
        .regex_replace('"max_retry_alloc_output_timeout": 10000,', '"max_retry_alloc_output_timeout": 0,'),
    ('vendor/etc/media_codecs_cape.xml', 'vendor/etc/media_codecs_cape_vendor.xml', 'vendor/etc/media_codecs_taro.xml', 'vendor/etc/media_codecs_taro_vendor.xml'): blob_fixup()
        .regex_replace('.*media_codecs_(google_audio|google_c2|google_telephony|vendor_audio).*\n', ''),
    'vendor/etc/msm_irqbalance.conf': blob_fixup()
        .regex_replace('IGNORED_IRQ=27,23,38$', 'IGNORED_IRQ=27,23,38,115,332'),
    ('vendor/bin/hw/android.hardware.gnss-aidl-service-qti', 'vendor/lib64/hw/android.hardware.gnss-aidl-impl-qti.so', 'vendor/lib64/libgarden.so', 'vendor/lib64/libgarden_haltests_e2e.so'): blob_fixup()
        .replace_needed('android.hardware.gnss-V1-ndk_platform.so', 'android.hardware.gnss-V1-ndk.so'),
    ('vendor/bin/hw/android.hardware.security.keymint-service-qti', 'vendor/lib64/libqtikeymint.so'): blob_fixup()
        .replace_needed('android.hardware.security.keymint-V1-ndk_platform.so', 'android.hardware.security.keymint-V1-ndk.so')
        .replace_needed('android.hardware.security.secureclock-V1-ndk_platform.so', 'android.hardware.security.secureclock-V1-ndk.so')
        .replace_needed('android.hardware.security.sharedsecret-V1-ndk_platform.so', 'android.hardware.security.sharedsecret-V1-ndk.so')
        .add_needed('android.hardware.security.rkp-V1-ndk.so'),
    ('vendor/lib64/libqcrilNr.so', 'vendor/lib64/libril-db.so'): blob_fixup()
        .binary_regex_replace(rb'persist\.vendor\.radio\.poweron_opt', rb'persist.vendor.radio.poweron_ign'),
    'vendor/lib64/vendor.libdpmframework.so': blob_fixup()
        .add_needed('libhidlbase_shim.so'),
}  # fmt: skip
module = ExtractUtilsModule(
    'sm8450-common',
    'oneplus',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

def patch_vendor_bp():
    print("\nApplying memory tagging bypasses to Android.bp...")

    # Resolve absolute path to the generated common Android.bp
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    bp_path = os.path.join(workspace_root, 'vendor', 'oneplus', 'sm8450-common', 'Android.bp')

    if os.path.isfile(bp_path):
        with open(bp_path, 'r') as f:
            content = f.read()

        # Inject Scudo TBI bypass for QSEECOM
        qseecom_target = 'name: "vendor.qti.hardware.qseecom@1.0-service",'
        if qseecom_target in content and 'memtag_heap: false' not in content:
            qseecom_patch = qseecom_target + '\n    sanitize: {\n        memtag_heap: false,\n    },'
            content = content.replace(qseecom_target, qseecom_patch)

        # Inject Scudo TBI bypass for Keymint
        keymint_target = 'name: "android.hardware.security.keymint-service-qti",'
        if keymint_target in content and 'memtag_heap: false' not in content:
            keymint_patch = keymint_target + '\n    sanitize: {\n        memtag_heap: false,\n    },'
            content = content.replace(keymint_target, keymint_patch)

        with open(bp_path, 'w') as f:
            f.write(content)

        print("Successfully patched sm8450-common vendor tree!")
    else:
        print(f"Warning: Could not find Android.bp at {bp_path}")

# Register the hook to run right as the script exits
atexit.register(patch_vendor_bp)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
