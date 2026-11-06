# Cài sprite-gen (aldegad/sprite-gen, Apache-2.0)

Nguồn: https://github.com/aldegad/sprite-gen. Đây là bản chép từ commit 4f5ccd5 (02/11/2026). Em đã bỏ thư mục `tests/` và `docs/assets/` (ảnh minh họa) cho nhẹ.

## Lần đầu dùng (chạy từ thư mục gốc của repo game)

```bash
cd .claude/skills/sprite-gen
python3 -m venv .venv && .venv/bin/pip install -e .
export SPRITE_GEN_ROOT="$(pwd)"
.venv/bin/sprite-gen --help
```

## Tạo ảnh mới cần một trong các tài khoản sau
- Codex CLI đăng nhập ChatGPT (`codex login`). Đây là mặc định.
- Grok CLI đã đăng nhập, hoặc biến `XAI_API_KEY`.
- OpenAI API key. Tính tiền mỗi lần gọi, chỉ dùng khi mình chọn.

## Không cần tài khoản nào
Các công cụ xử lý ảnh vẫn chạy với ảnh làm từ ArtCraft:
- `cutout`: tách nền
- `slice-sheet`: cắt sheet thành từng frame
- `compose-atlas`: ghép atlas
- `recolor`: đổi màu
- `export-pngs`, `export-aseprite`: xuất ảnh
- `background-tile`: làm nền lặp
- `shadow`: đổ bóng
