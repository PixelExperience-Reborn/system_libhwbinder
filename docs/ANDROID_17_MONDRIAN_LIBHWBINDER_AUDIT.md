# P1 — Android17 libhwbinder / mondrian HIDL IPC compatibility audit

Date: 2026-11-04. Source-only audit; **no Android17 libhwbinder replacement and no device runtime tests**.

## Historical PE evidence

- Historical PixelExperience-Reborn `system_libhwbinder` branch `seventeen`, HEAD `af0273b65326de3923631d2e415aa5b7af9c20a7`.
- Its HEAD patch **reverts** upstream check disallowing HIDL binder threadpool shrink after start; the original commit describes camera problems on **kona/lahaina**, **not mondrian**. `ProcessState::setThreadPoolConfiguration` in archived PE therefore does *not* contain the `LOG_ALWAYS_FATAL_IF(mThreadPoolStarted && maxThreads < mMaxThreads)` guard. The old reason is device-specific and does not justify platform-wide changes for Android17 mondrian.
- `487bee35e0416f6aa7c79c5e1f1a184f92609d43` adds a userland `Parcel::verifyBufferObject` bound check `parent >= mObjectsSize`, complementing kernel validation and preventing fuzzer crashes. The archived tree includes this protection. **Do not remove it** while porting any code.
- Old Soong still builds `libhwbinder-impl-internal`, `libhwbinder_headers`, deprecated `libhwbinder` compatibility module, and `hwbinder_lto`; this IPC implementation is statically integrated into `libhidlbase`.

## Official AOSP17 r1 contract

- Official `platform/system/libhwbinder` Git tree `901e90f23d898265adf60c8645216ede9b308a27` from https://android.googlesource.com/platform/system/libhwbinder/+/refs/tags/android-17.0.0_r1/ .
- Official `Android.bp` includes `libutils_headers` on the `libhwbinder_headers` path, has modern `libhwbinder-impl-internal` APEX allowlist (including `com.android.bt`, `com.android.nfcservices`, `com.android.tethering`), and its implementation is used by `libhidlbase`. These Soong declarations are *not* the same graph as the historical archive.
- The upstream AOSP17 `ProcessState::setThreadPoolConfiguration` **retains** the guard rejecting shrink after threadpool start. This old PE revert must **not** be cherry-picked: a global permissive change masks inconsistent runtime threading and can affect IPC for multiple unrelated HALs.
- Upstream AOSP17 `Parcel.cpp` should preserve the parent-index bounds check; see test gate below. Do not touch parcel verification or binder security.
- The official `platform/system/libhwbinder` path and companion `platform/system/libhidl`, `platform/hardware/interfaces`, `platform/system/core` are retained in the staged AOSP17 manifest.

## Mondrian independent ROM release gates

1. Build new native PE-Reborn `device/xiaomi/mondrian` and `device/xiaomi/sm8450-common` product trees, using older LF52406 LineageOS-derived trees as **hardware reference only**.
2. Inventory each proprietary HIDL HAL and actual `/dev/hwbinder` producer/consumer; check binder driver features/ABI and kernel5.10 compatibility. No assumption that a kona/lahaina camera issue exists on mondrian.
3. Validate `libhidlbase` and `libhwbinder-impl-internal` Soong graph, partition/vendor/APEX visibility and VINTF mappings. Review binder threadpool sizing and deadlock/crash behavior with test HALs.
4. Run official binder/parcel fuzzers and VTS HIDL/IPC tests; verify actual camera/audio/radio/NFC/KeyMint and recovery services, SELinux/hwservicemanager registration and reboot stability.
5. Confirm exact tagged upstream Git tree (source-only CI), then full Android17 compile and real mondrian hardware tests separately.

## Current result

- [x] Historical threadpool-shrink revert and parent-index bounds check identified.
- [x] AOSP17 upstream changes / exact Git tree identified.
- [x] Historical PE threadpool/Parcel source CI [PASS #41793411252](https://github.com/PixelExperience-Reborn/system_libhwbinder/actions/runs/41793411252).
- [x] Official Android17 r1 exact Git tree, threadpool guard, Parcel parent bounds and modern Soong source CI [PASS #41793411198](https://github.com/PixelExperience-Reborn/system_libhwbinder/actions/runs/41793411198). **Source-level only**, not full Binder device validation.
- [ ] Android17 Soong/libhidl ABI link build, VINTF/CTS/VTS/fuzzer and physical mondrian testing.
- [ ] Real vendor blob and kernel compatibility validation.

**Decision:** no old PE libhwbinder replacement or device-irrelevant camera workaround. Keep AOSP17 IPC and security checks.
