/*
 * Copyright (C) 2024 LibreMobileOS Foundation
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include "CameraProviderExtension.h"

#include <fstream>
#include <unistd.h>
#include <android-base/properties.h>
#include <string>

static const std::string kTorchBrightness = "brightness";
static const std::string kTorchMaxBrightness = "max_brightness";
static const std::string kToggleSwitchPath = "/sys/devices/platform/soc/c42d000.qcom,spmi/spmi-0/0-02/c42d000.qcom,spmi:qcom,pm8350c@2:qcom,flash_led@ee00/leds/led:switch_1/brightness";

static std::string kTorchLedPaths[] = {
    "/sys/devices/platform/soc/c42d000.qcom,spmi/spmi-0/0-02/c42d000.qcom,spmi:qcom,pm8350c@2:qcom,flash_led@ee00/leds/led:torch_0",
    "/sys/devices/platform/soc/c42d000.qcom,spmi/spmi-0/0-02/c42d000.qcom,spmi:qcom,pm8350c@2:qcom,flash_led@ee00/leds/led:torch_1",
    "/sys/devices/platform/soc/c42d000.qcom,spmi/spmi-0/0-02/c42d000.qcom,spmi:qcom,pm8350c@2:qcom,flash_led@ee00/leds/led:torch_2",
    "/sys/devices/platform/soc/c42d000.qcom,spmi/spmi-0/0-02/c42d000.qcom,spmi:qcom,pm8350c@2:qcom,flash_led@ee00/leds/led:torch_3",
};

/**
 * Write value to path, explicitly flush, and close file.
 */
template <typename T>
static void set(const std::string& path, const T& value) {
    std::ofstream file(path);
    if (file.is_open()) {
        file << value;
        file.flush();
        file.close();
    }
}

/**
 * Read value from the path and close file.
 */
template <typename T>
static T get(const std::string& path, const T& def) {
    std::ifstream file(path);
    T result;

    file >> result;
    if (file.is_open()) {
        file.close();
    }
    return file.fail() ? def : result;
}

bool supportsTorchStrengthControlExt() {
    return true;
}

bool supportsSetTorchModeExt() {
    return false;
}

int32_t getTorchMaxStrengthLevelExt() {
    // SAFE FIX: Read the actual safe maximum from the kernel node.
    // If the node can't be read, fallback to a safe 200.
    auto node = kTorchLedPaths[0] + "/" + kTorchMaxBrightness;
    return get(node, 200);
}

int32_t getTorchDefaultStrengthLevelExt() {
    // Dynamically set default to whatever the current max is.
    return getTorchMaxStrengthLevelExt();
}

int32_t getTorchStrengthLevelExt() {
    auto node = kTorchLedPaths[0] + "/" + kTorchBrightness;
    return get(node, 0);
}

void setTorchStrengthLevelExt(int32_t torchStrength, bool enabled) {
    if (!enabled) {
        android::base::SetProperty("camera.torch.enabled", "0");

        // Graceful Step-Down Sequence (Prevents PMIC panic)
        for (const auto& path : kTorchLedPaths) {
            set(path + "/" + kTorchBrightness, 0);
        }

        // Kill the master switch only after LDOs are zeroed
        set(kToggleSwitchPath, 0);
        return;
    }

    android::base::SetProperty("camera.torch.level", std::to_string(torchStrength));
    android::base::SetProperty("camera.torch.enabled", "1");

    // We no longer force max_brightness. We respect the kernel limits.
    for (const auto& path : kTorchLedPaths) {
        set(path + "/" + kTorchBrightness, torchStrength);
    }

    // Commit the brightness targets
    set(kToggleSwitchPath, 1);
}

void setTorchModeExt(bool enabled) {
    int32_t strength = getTorchDefaultStrengthLevelExt();
    setTorchStrengthLevelExt(enabled ? strength : 0, enabled);
}
