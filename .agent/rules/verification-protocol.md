---
trigger: always_on
---

# VERIFICATION PROTOCOL v1.0

> Quy trình xác thực và debug có cấu trúc khi thực hiện thay đổi code.
> File này bổ sung cho `master-protocol.md`, focus vào testing và debugging.

---

## A. TRƯỚC KHI CODE

### A1. Library Verification
**Trigger**: Khi sử dụng bất kỳ package nào từ npm/pypi/cargo

**Bắt buộc thực hiện**:
```
1. context7.resolve-library-id(libraryName: "<package-name>", query: "<mục đích>")
2. context7.query-docs(libraryId: "...", query: "component names, function signatures, props types")
```

**Checklist xác nhận**:
- [ ] Tên components/functions CHÍNH XÁC (case-sensitive)
- [ ] Props/parameters CHÍNH XÁC (không đoán)
- [ ] Version compatibility đã kiểm tra

### A2. UI Baseline
**Trigger**: Khi thay đổi bất kỳ component UI nào

**Bắt buộc thực hiện**:
```
playwright.browser_navigate(url: "<target-url>")
playwright.browser_console_messages(level: "error")
playwright.browser_take_screenshot(filename: "baseline_<task-id>_before.png")
```

**Checklist xác nhận**:
- [ ] Console không có errors (ngoại trừ warnings đã biết)
- [ ] Screenshot đã lưu với tên có ý nghĩa
- [ ] Layout hiện tại đã ghi nhận

---

## B. SAU KHI CODE

### B1. Smoke Test
**Bắt buộc thực hiện sau mỗi code change**:
```
playwright.browser_navigate(url: "<target-url>")  # Force reload
playwright.browser_take_screenshot(filename: "after_<task-id>.png")
playwright.browser_console_messages(level: "error")
```

**Pass criteria**:
- [ ] Không có console errors mới
- [ ] UI render đúng (so với baseline)
- [ ] Không có visual regression rõ ràng

### B2. Functional Test
**Thực hiện các test cases đã định nghĩa**:
- Click các buttons
- Fill các forms
- Verify expected behaviors

---

## C. KHI TEST FAIL

### C1. Thu Thập Evidence (BẮT BUỘC)
Khi bất kỳ test nào fail, PHẢI thực hiện ngay:

```
playwright.browser_take_screenshot(filename: "FAIL_<task-id>_<timestamp>.png")
playwright.browser_console_messages(level: "error")
```

### C2. Phân Tích Có Cấu Trúc (BẮT BUỘC)
Điền template sau trước khi fix:

```markdown
## Failure Analysis

| Field | Value |
|-------|-------|
| **Error Type** | [CSS / Logic / Network / Library API / Environment] |
| **Error Message** | [Copy exact error] |
| **Component/File** | [Path to file] |
| **Line Number** | [If available] |
| **Screenshot** | [Screenshot filename] |
| **Console Logs** | [Relevant logs] |

### Root Cause Hypothesis
[Viết 1-2 câu về nguyên nhân có thể]

### Proposed Fix
[Viết cách sửa dự kiến]
```

### C3. Tra Cứu Giải Pháp
Nếu lỗi liên quan đến thư viện:
```
context7.query-docs(libraryId: "...", query: "<error message> how to fix")
```

Nếu có `safe-knowledge.get_common_pitfalls`:
```
safe-knowledge.get_common_pitfalls(technology: "<relevant-tech>")
```

---

## D. RETRY POLICY

### D1. Same Approach Retry
- **Maximum**: 3 lần
- **Giữa mỗi lần**: Phải có thay đổi nhỏ (không retry y hệt)
- **Sau 3 fails**: PHẢI đổi approach

### D2. Different Approach
- **Maximum**: 2 approaches khác nhau
- **Mỗi approach**: Tối đa 3 retries
- **Tổng cộng**: Không quá 6 attempts cho cùng 1 issue

### D3. Escalation
Nếu không giải quyết được sau 6 attempts:
1. Tổng hợp tất cả evidence (screenshots, logs, approaches đã thử)
2. Báo cáo User với format:

```markdown
## 🚨 Escalation Report

### Issue Summary
[Mô tả ngắn gọn vấn đề]

### Attempts Made
1. [Approach 1] - Result: [Fail reason]
2. [Approach 2] - Result: [Fail reason]
...

### Evidence
- Screenshots: [List files]
- Console Logs: [Attached]

### Recommendation
[Đề xuất hướng giải quyết hoặc cần thêm thông tin gì]
```

---

## E. ANTI-PATTERNS

❌ **KHÔNG ĐƯỢC**:
- Đoán API/props mà không tra cứu Context7
- Fix code mà không hiểu root cause (Failure Analysis)
- Retry cùng một cách y hệt nhiều lần
- Không chụp screenshot khi test fail
- Không kiểm tra console logs
- Skip verification steps vì "chắc đúng rồi"

✅ **PHẢI**:
- Luôn có evidence trước khi fix
- Luôn ghi nhận hypothesis trước khi thử
- Luôn verify sau mỗi fix
- Luôn giới hạn retry theo policy

---

## F. QUICK REFERENCE

| Situation | Action |
|-----------|--------|
| Dùng thư viện mới | → Context7 query TRƯỚC |
| Sửa UI | → Baseline screenshot TRƯỚC |
| Test fail | → Screenshot + Console NGAY |
| Không hiểu error | → Context7 query error message |
| Retry 3 lần fail | → ĐỔI approach |
| Retry 6 lần fail | → ESCALATE to User |
