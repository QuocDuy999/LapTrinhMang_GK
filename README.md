# LapTrinhMang_GK
Đề Tài Trò Chơi Cờ Vua sử dụng kỹ thuật lập trình Socket theo mô hình Multi Client-Server 
Dự án này là **trò chơi cờ vua trực tuyến (Online Chess)** được xây dựng bằng **Python Socket** theo mô hình **Client–Server**.  
Hai người chơi có thể đấu với nhau **trên cùng mạng LAN hoặc Wi-Fi**.  
Giao diện được tạo bằng **Tkinter**, logic cờ sử dụng thư viện **python-chess**, và hình ảnh quân cờ được lấy từ thư mục `assets/`.

---

## 🧩 Tính năng nổi bật

- 🎮 **2 người chơi đấu trực tuyến qua mạng LAN/Wi-Fi**  
- 🧠 **Tuân thủ đầy đủ luật cờ vua FIDE**, kiểm tra hợp lệ từng nước đi  
- ⚔️ **Tự động phân vai**: người vào trước là **Trắng**, người sau là **Đen**  
- 👑 **Phát hiện trạng thái ván đấu**: Checkmate, Stalemate, hoặc Draw  
- 🖼️ **Giao diện trực quan** sử dụng Tkinter + hình ảnh PNG sắc nét  
- 🗣️ **Hiển thị thông báo** khi ván đấu kết thúc hoặc người chơi thoát  

---

## 📁 Cấu trúc thư mục
```bash
📦 Online-Chess
├── 🧠 server.py          # File server – chạy trên máy chủ
├── 🎮 client.py          # File client – chạy trên mỗi người chơi
├── 🖼️ assets/            # Thư mục chứa hình ảnh quân cờ PNG
│   ├── ♔ king_white.png
│   ├── ♛ queen_black.png
│   └── ...
└── 📘 README.md          # Tài liệu mô tả dự án
```
---
<img width="1919" height="1021" alt="image" src="https://github.com/user-attachments/assets/b25a1c66-680a-479b-b90f-b6b5e4cf41c5" />
