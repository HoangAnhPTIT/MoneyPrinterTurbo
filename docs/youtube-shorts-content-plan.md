# Kế hoạch nội dung YouTube Shorts — A/B Testing 10 video (Tiếng Việt)

**Ngày:** 2026-05-30
**Công cụ:** MoneyPrinterTurbo — **Standard flow** (script AI + giọng đọc + stock footage + phụ đề)
**Mục tiêu:** Kiếm tiền từ YouTube Shorts. Đăng 10 video trải trên 5 ngách "hot" để **A/B test tìm ngách ăn nhất**, rồi dồn lực vào ngách thắng.
**Ngôn ngữ:** Tiếng Việt | **Định dạng:** 9:16, 1080×1920, ~40–55s/video.

---

## 0. ⚠️ CẤU HÌNH BẮT BUỘC trước khi gen (đọc kỹ phần này)

> Nếu để mặc định rồi bấm gen, **phụ đề tiếng Việt sẽ vỡ chữ (□)**. Đã kiểm chứng bằng cách quét glyph từng font.

| Thiết lập | Giá trị | Lý do |
|---|---|---|
| **Font phụ đề** | `DejaVuSans.ttf` (dùng ngay) **hoặc** `BeVietnamPro-Bold.ttf` (đẹp nhất, tự thêm vào `resource/fonts/`) | Font mặc định `STHeitiMedium.ttc` / `MicrosoftYaHeiBold.ttc` là **font Trung, THIẾU dấu tiếng Việt** (ế ộ ữ ằ ơ ư...). |
| **Tỉ lệ khung** | **Portrait 9:16 (1080×1920)** | Chuẩn YouTube Shorts. |
| **Giọng đọc** | `vi-VN-HoaiMyNeural-Female` (nữ) hoặc `vi-VN-NamMinhNeural-Male` (nam) | Giọng edge-tts tiếng Việt tự nhiên. |
| **Video Language** | để trống (auto-detect) → tự nhận tiếng Việt | Khớp giọng vi-VN. |
| **Font size** | ~72–80 | Đọc rõ trên màn hình dọc. |
| **Màu chữ / viền** | Chữ **trắng** + viền (stroke) **đen**, độ dày ~4–5 | Đọc rõ trên mọi nền footage. |
| **Nhạc nền (BGM)** | Bật, âm lượng thấp (~0.1–0.2) | Giữ năng lượng, không át giọng đọc. |

**Font khuyến nghị (chọn 1, đều miễn phí, license OFL):**
- **Be Vietnam Pro** (Bold/ExtraBold) — thiết kế riêng cho tiếng Việt, hiện đại, đậm. **Tốt nhất.**
- **Montserrat** (Bold/Black) — font caption Shorts phổ biến nhất thế giới, có subset tiếng Việt.
- **Noto Sans** (Bold) — phủ tiếng Việt tuyệt đối, sạch sẽ.

> Cách thêm font: tải file `.ttf` → copy vào `resource/fonts/` → khởi động lại WebUI → font xuất hiện trong dropdown **Font**.

---

## 1. Cách dùng plan này với MoneyPrinterTurbo

Mỗi video bên dưới có sẵn 3 ô để **dán thẳng** vào WebUI:

1. **Video Subject** → ô *Video Subject* (chủ đề ngắn).
2. **Video Script** → ô *Video Script* (kịch bản đầy đủ — **dán cái này vào là KHÔNG cần bấm "Generate Script"**, hệ thống dùng luôn).
3. **Video Keywords** → ô *Video Keywords* (từ khoá **tiếng Anh**, phẩy ngăn cách — để Pexels/Pixabay tìm được nhiều footage chất lượng; thư viện stock index theo tiếng Anh nên tiếng Anh cho kết quả tốt hơn hẳn).

Rồi đặt các thiết lập ở **Mục 0** → bấm **Generate Video**.

---

## 2. Bảng tổng quan 10 video (5 ngách × 2)

| # | Ngách | Tiêu đề | Đòn bẩy tâm lý |
|---|-------|---------|----------------|
| 1 | 🧠 Facts/Khoa học | Não bạn tự "xoá" ký ức khi qua cửa | Tò mò + liên quan bản thân |
| 2 | 🧠 Facts/Khoa học | 1 thìa sao neutron nặng 4 tỷ tấn | Sốc + quy mô khó tin |
| 3 | 💬 Tâm lý đời thường | Người EQ cao không bao giờ nói câu này | Tò mò + ứng dụng ngay |
| 4 | 💬 Tâm lý đời thường | Mẹo khiến ai cũng quý bạn (Ben Franklin) | Nghịch lý + hữu ích |
| 5 | 💰 Tiền & tài chính | Quy tắc 50/30/20 quản lý lương | Sợ nghèo + hành động ngay |
| 6 | 💰 Tiền & tài chính | Lãi kép — kỳ quan thứ 8 | Tham vọng + con số gây sốc |
| 7 | 🌊 Lịch sử & bí ẩn | 80% đại dương chưa ai từng thấy | Bí ẩn + sợ hãi nhẹ |
| 8 | 🌊 Lịch sử & bí ẩn | Nền văn minh biến mất sau 1 đêm | Bí ẩn chưa lời giải |
| 9 | 🤖 Công nghệ & AI | 5 công cụ AI miễn phí làm thay cả đội | Lợi ích + FOMO |
| 10 | 🤖 Công nghệ & AI | 1 câu thần chú giúp ChatGPT thông minh gấp 10× | Bí kíp + ứng dụng ngay |

---

## 3. Chi tiết 10 video

> Mỗi script ~115–140 từ ≈ 40–55s khi đọc bằng giọng vi-VN. Cấu trúc: **Hook (0–3s) → Triển khai → Cú chốt → Vòng lặp/CTA**.

---

### 🧠 NGÁCH 1 — FACTS / KHOA HỌC

#### Video 1 — Não bạn tự "xoá" ký ức khi bước qua cửa

- **Hook (0–3s):** *"Bước vào phòng rồi quên mất định làm gì? Não bạn vừa cố ý xoá ký ức đấy."*

**Video Subject:**
```
Hiệu ứng tâm lý "doorway effect" — vì sao ta hay quên khi bước qua cửa
```

**Video Script:**
```
Bạn bước vào phòng, rồi đứng ngẩn ra, quên mất mình định làm gì? Đừng lo, não bạn không hỏng đâu. Các nhà khoa học gọi đây là "hiệu ứng ô cửa". Mỗi khi bạn đi qua một ngưỡng cửa, não tự động đóng gói ký ức của căn phòng cũ lại, để dọn chỗ cho không gian mới. Việc bạn định làm bị xếp nhầm vào phòng cũ, thế là nó biến mất. Cách khắc phục? Nói to dự định trước khi bước đi, hoặc quay lại đúng chỗ cũ, ký ức sẽ ùa về ngay. Não bạn vừa lừa bạn một vố đấy. Còn điều gì về bộ não khiến bạn bất ngờ nữa? Theo dõi để biết thêm nhé.
```

**Video Keywords:**
```
person walking through doorway, open door home, empty modern room, confused thinking person, brain animation glowing, hallway interior, forgetful man
```

- **Hashtag/Caption:** `#tamly #naobo #factshay #biquyet #shorts` — *"Hoá ra không phải bạn đãng trí 😳 #tamly"*
- **Vì sao hot:** Ai cũng từng trải nghiệm → cực dễ đồng cảm + share. Hook chạm đúng "nỗi đau" quen thuộc.
- **Biến thể A/B:** Đổi tiêu đề thành *"Vì sao bạn quên ngay khi bước vào phòng?"* (dạng câu hỏi) để test câu khẳng định vs câu hỏi.

---

#### Video 2 — 1 thìa sao neutron nặng 4 tỷ tấn

- **Hook (0–3s):** *"Một thìa cà phê thứ này nặng hơn cả ngọn núi Everest — và nó có thật."*

**Video Subject:**
```
Sao neutron — vì sao một thìa vật chất nặng hàng tỷ tấn
```

**Video Script:**
```
Một thìa cà phê thứ này nặng hơn cả ngọn núi Everest. Không phải khoa học viễn tưởng, đó là sao neutron. Khi một ngôi sao khổng lồ chết đi, nó sụp đổ vào chính mình, nén cả khối lượng gấp đôi Mặt Trời vào một quả cầu chỉ rộng khoảng hai mươi ki-lô-mét, bằng một thành phố nhỏ. Vật chất bị ép chặt đến mức một thìa nhỏ nặng tới bốn tỷ tấn. Nếu thả nó xuống Trái Đất, nó sẽ xuyên thẳng qua hành tinh như xuyên qua giấy. Và điên rồ hơn, sao neutron quay tới bảy trăm vòng mỗi giây. Vũ trụ ngoài kia còn nhiều thứ khó tin hơn thế. Bạn muốn xem cái nào tiếp theo?
```

**Video Keywords:**
```
neutron star space, galaxy stars cosmos, supernova exploding star, spinning planet, deep universe nebula, mount everest peak, black hole, astronomy
```

- **Hashtag/Caption:** `#vutru #khoahoc #saoneutron #factshay #shorts` — *"4 tỷ tấn trong 1 thìa 🤯 #vutru"*
- **Vì sao hot:** Quy mô gây sốc + footage vũ trụ luôn đẹp/đa dạng trên Pexels → video lên hình ấn tượng.
- **Biến thể A/B:** Test mở đầu bằng con số *"700 vòng mỗi giây..."* thay vì so sánh Everest.

---

### 💬 NGÁCH 2 — TÂM LÝ ĐỜI THƯỜNG

#### Video 3 — Người EQ cao không bao giờ nói câu này

- **Hook (0–3s):** *"Người thông minh cảm xúc tuyệt đối tránh câu này khi cãi nhau."*

**Video Subject:**
```
Trí tuệ cảm xúc — câu nói người EQ cao luôn tránh khi tranh cãi
```

**Video Script:**
```
Người thông minh cảm xúc không bao giờ nói câu này khi cãi nhau, đó là: "Bình tĩnh lại đi". Nghe có vẻ vô hại, nhưng nó như xăng đổ vào lửa. Vì sao? Khi bạn bảo ai đó bình tĩnh, não họ hiểu ngầm là: cảm xúc của mày không hợp lý. Lập tức họ phòng thủ và còn nóng hơn. Người EQ cao làm ngược lại, họ gọi tên cảm xúc: "Anh thấy em đang rất bực, đúng không?". Chỉ một câu công nhận thôi, cơn giận hạ nhiệt thấy rõ. Nguyên tắc vàng là: muốn ai đó bình tĩnh, đừng ra lệnh, hãy khiến họ thấy được thấu hiểu. Lần tới bạn sẽ thử câu nào? Lưu lại để dùng nhé.
```

**Video Keywords:**
```
two people arguing, couple serious conversation, calm discussion talking, person listening empathy, emotional angry face, conflict resolution, close up talking
```

- **Hashtag/Caption:** `#EQ #tritueQcamxuc #giaotiep #tamly #shorts` — *"Câu nói tưởng vô hại 👀 #EQ"*
- **Vì sao hot:** Ứng dụng được NGAY trong đời thực → lưu/chia sẻ cao. Niche tâm lý dễ viral trên Shorts VN.
- **Biến thể A/B:** Test tiêu đề liệt kê *"3 câu người EQ cao không bao giờ nói"* (dạng listicle) vs đơn lẻ.

---

#### Video 4 — Mẹo khiến ai cũng quý bạn (Hiệu ứng Ben Franklin)

- **Hook (0–3s):** *"Muốn ai quý bạn? Đừng giúp họ — hãy NHỜ họ giúp bạn."*

**Video Subject:**
```
Hiệu ứng Ben Franklin — vì sao nhờ vả lại khiến người ta quý bạn hơn
```

**Video Script:**
```
Muốn ai đó quý bạn? Đừng giúp họ, hãy nhờ họ giúp bạn một việc nhỏ. Nghe ngược đời, nhưng tâm lý học đã chứng minh suốt hơn hai trăm năm. Chuyện kể rằng Benjamin Franklin muốn lấy lòng một đối thủ. Ông không tặng quà, mà mượn một cuốn sách hiếm. Sau khi cho mượn, người kia bỗng quý Franklin, rồi hai người thành bạn thân. Vì sao lại thế? Não chúng ta ghét mâu thuẫn. Khi đã giúp bạn, não tự nhủ: chắc mình quý người này nên mới giúp. Một lời nhờ nhỏ tạo ra thiện cảm lớn. Lần tới gặp người bạn muốn thân hơn, hãy nhờ một việc tí xíu thôi. Thử xem có đúng không nhé.
```

**Video Keywords:**
```
Benjamin Franklin portrait vintage, lending old book, friends handshake, two colleagues helping, library books, people smiling talking, asking favor office
```

- **Hashtag/Caption:** `#tamlyhoc #kynanggiaotiep #benfranklin #factshay #shorts`
- **Vì sao hot:** "Mẹo ngược đời" tạo curiosity gap mạnh + có câu chuyện lịch sử để kể → giữ chân tốt.
- **Biến thể A/B:** Test hook bằng câu hỏi *"Vì sao càng nhờ vả, người ta càng quý bạn?"*.

---

### 💰 NGÁCH 3 — TIỀN & TÀI CHÍNH CÁ NHÂN

#### Video 5 — Quy tắc 50/30/20 quản lý lương

- **Hook (0–3s):** *"Lương vừa về? Làm bước này trước khi tiêu 1 đồng, nếu không bạn nghèo cả đời."*

**Video Subject:**
```
Quy tắc 50/30/20 — cách chia tiền lương để không cháy túi
```

**Video Script:**
```
Lương vừa về tài khoản? Khoan tiêu vội. Làm bước này trước, nếu không bạn sẽ cháy túi cuối tháng cả đời. Đây là quy tắc năm mươi, ba mươi, hai mươi mà người quản lý tiền giỏi luôn dùng. Ngay khi nhận lương, chia làm ba phần. Năm mươi phần trăm cho nhu cầu thiết yếu: ăn ở, đi lại, hoá đơn. Ba mươi phần trăm cho mong muốn: cà phê, mua sắm, giải trí. Và hai mươi phần trăm, quan trọng nhất, chuyển thẳng vào tiết kiệm và đầu tư, trước khi tiêu phần còn lại. Mẹo nhỏ: cài chuyển khoản tự động hai mươi phần trăm ngay ngày nhận lương, để khỏi bị cám dỗ. Hãy trả tiền cho tương lai của bạn trước tiên. Bạn đang để dành bao nhiêu phần trăm?
```

**Video Keywords:**
```
counting money cash, salary payday envelope, piggy bank savings, budgeting notebook calculator, coins stacking, mobile banking app, investment growth, financial planning
```

- **Hashtag/Caption:** `#quanlytaichinh #tietkiem #tienbac #quytac503020 #shorts` — *"Bí quyết không bao giờ cháy túi 💰"*
- **Vì sao hot:** Ngách tài chính có **RPM cao nhất** (~$4.5 CPM). Chủ đề "đau ví" ai cũng quan tâm.
- **Biến thể A/B:** Test tiêu đề *"Người giàu chia lương khác bạn thế nào?"* (so sánh) vs công thức.

---

#### Video 6 — Lãi kép, kỳ quan thứ 8

- **Hook (0–3s):** *"1 triệu mỗi tháng có thể thành cả tỷ. Bí mật nằm ở một con số bạn đang bỏ qua."*

**Video Subject:**
```
Lãi kép — sức mạnh khiến tiền tự sinh ra tiền theo thời gian
```

**Video Script:**
```
Einstein gọi nó là kỳ quan thứ tám của thế giới. Và nó có thể biến vài triệu mỗi tháng của bạn thành cả tỷ đồng. Đó là lãi kép. Lãi đơn là tiền đẻ ra tiền. Còn lãi kép là tiền đẻ ra tiền, rồi chính số tiền mới đó lại tiếp tục đẻ tiếp, như quả cầu tuyết lăn xuống dốc, càng lăn càng to. Ví dụ: bạn để dành ba triệu mỗi tháng, lãi mười phần trăm một năm. Sau ba mươi năm, bạn không chỉ có hơn một tỷ tiền gốc, mà có tới hơn sáu tỷ. Phần lớn là lãi đẻ ra lãi. Bí mật lớn nhất ở đây là gì? Là thời gian. Bắt đầu càng sớm, bạn càng giàu. Và hôm nay chính là ngày sớm nhất mà bạn có thể bắt đầu.
```

**Video Keywords:**
```
compound interest chart growth, snowball rolling downhill, money growing graph, coins plant tree, savings rising, stock market uptrend, financial freedom, calculator finance
```

- **Hashtag/Caption:** `#laikep #dautu #taichinhcanhan #lamgiau #shorts`
- **Vì sao hot:** Con số "6 tỷ" gây sốc + cảm giác cấp bách ("bắt đầu sớm") → thúc đẩy hành động & lưu.
- **Biến thể A/B:** Test có/không nhắc tên Einstein ở hook (uy tín vs thẳng vào con số).

---

### 🌊 NGÁCH 4 — LỊCH SỬ & BÍ ẨN THẾ GIỚI

#### Video 7 — 80% đại dương chưa ai từng thấy

- **Hook (0–3s):** *"Ta biết bề mặt Sao Hoả rõ hơn đáy biển của chính Trái Đất. Dưới đó có gì?"*

**Video Subject:**
```
Bí ẩn đáy đại dương — vì sao phần lớn vẫn chưa được khám phá
```

**Video Script:**
```
Con người biết về bề mặt Sao Hoả rõ hơn cả đáy biển của chính Trái Đất. Nghe khó tin? Hơn tám mươi phần trăm đại dương chưa từng được lập bản đồ hay nhìn thấy bằng mắt người. Càng xuống sâu, áp suất càng khủng khiếp, đủ sức bóp bẹp một chiếc tàu ngầm như bóp vỏ lon. Dưới đó, trong bóng tối tuyệt đối, là những sinh vật tự phát sáng kỳ dị, những dãy núi cao hơn cả Everest, và cả những loài mà khoa học chưa từng đặt tên. Nơi sâu nhất, vực Mariana, sâu gần mười một ki-lô-mét. Thả cả đỉnh Everest xuống đó vẫn còn dư nước phía trên. Hành tinh bí ẩn nhất hoá ra ở ngay đây, chính là đại dương. Bạn có dám lặn xuống không?
```

**Video Keywords:**
```
deep ocean dark water, underwater abyss blue, bioluminescent sea creature, submarine descending, mariana trench, ocean waves aerial drone, deep sea fish glowing, sonar
```

- **Hashtag/Caption:** `#daiduong #bian #khoahoc #marianatrench #shorts` — *"Nơi đáng sợ nhất hành tinh 🌊"*
- **Vì sao hot:** Bí ẩn + sợ hãi nhẹ = retention rất cao. Footage biển sâu trên Pexels đẹp và nhiều.
- **Biến thể A/B:** Test hook *"Thứ đáng sợ nhất hành tinh không nằm trong vũ trụ..."*.

---

#### Video 8 — Nền văn minh biến mất sau 1 đêm

- **Hook (0–3s):** *"Một thành phố 4.000 năm tuổi bốc hơi sau một đêm. Không ai biết vì sao."*

**Video Subject:**
```
Nền văn minh sông Ấn — vì sao biến mất một cách bí ẩn
```

**Video Script:**
```
Một nền văn minh bốn nghìn năm tuổi, đông dân hơn cả Ai Cập cổ đại, bỗng biến mất gần như sau một đêm. Đến nay vẫn không ai biết chắc vì sao. Đó là nền văn minh sông Ấn. Họ xây những thành phố ngăn nắp đến kinh ngạc: đường lát gạch thẳng tắp, hệ thống thoát nước và cả nhà vệ sinh, có trước người La Mã hàng nghìn năm. Rồi đột nhiên, các thành phố bị bỏ hoang, không một dấu vết chiến tranh. Giả thuyết hàng đầu là một con sông lớn đổi dòng rồi cạn khô, khiến mùa màng sụp đổ. Và đáng sợ nhất: chữ viết của họ đến giờ vẫn chưa ai giải mã được. Cả một dân tộc, im lặng mãi mãi. Lịch sử còn đang giấu chúng ta điều gì nữa?
```

**Video Keywords:**
```
ancient ruins city aerial, archaeology excavation site, dried cracked river bed, old brick street ruins, lost civilization, ancient artifacts pottery, desert ruins, mysterious carving
```

- **Hashtag/Caption:** `#lichsu #bian #vanminhcodai #songan #shorts`
- **Vì sao hot:** "Chưa lời giải" = vòng tò mò không khép → người xem bình luận tranh luận → tăng tương tác.
- **Biến thể A/B:** Test kết bằng câu hỏi mời bình luận giả thuyết vs câu cảm thán.

---

### 🤖 NGÁCH 5 — CÔNG NGHỆ & AI

#### Video 9 — 5 công cụ AI miễn phí làm thay cả đội

- **Hook (0–3s):** *"Công cụ AI này làm trong 10 giây việc bạn từng mất cả ngày — và nó miễn phí."*

**Video Subject:**
```
5 công cụ AI miễn phí giúp làm việc nhanh gấp nhiều lần
```

**Video Script:**
```
Năm công cụ AI miễn phí này làm trong mười giây những việc bạn từng mất cả ngày. Một: ChatGPT, viết email, lên kế hoạch, tóm tắt tài liệu dài thành vài dòng. Hai: công cụ tách nền ảnh tự động, không cần Photoshop, chỉ một cú nhấp chuột. Ba: công cụ chuyển văn bản thành giọng nói y như người thật, làm video mà không cần lộ mặt. Bốn: AI tạo slide thuyết trình hoàn chỉnh chỉ từ một câu mô tả. Năm: trợ lý gỡ lỗi code, dán đoạn lỗi vào là nó chỉ ngay chỗ sai. Tất cả đều có bản dùng miễn phí. AI sẽ không thay thế bạn đâu, nhưng người biết dùng AI thì có đấy. Bạn muốn mình hướng dẫn kỹ công cụ nào? Theo dõi để xem phần hai nhé.
```

**Video Keywords:**
```
artificial intelligence interface, laptop working fast typing, AI chatbot screen, automation technology futuristic, productivity workspace desk, robot assistant, software dashboard, tech innovation
```

- **Hashtag/Caption:** `#AI #congcuAI #congnghe #nangsuat #shorts` — *"Lưu lại kẻo mất 🔖 #AI"*
- **Vì sao hot:** Ngách AI **tăng trưởng nhanh nhất 2026** + bạn có nền tảng tech → QC chuẩn. CTA "phần 2" tạo chuỗi.
- **Biến thể A/B:** Test "5 công cụ" vs "3 công cụ" (ít hơn = cảm giác dễ nhớ/đỡ ngợp).

---

#### Video 10 — 1 câu thần chú giúp ChatGPT thông minh gấp 10×

- **Hook (0–3s):** *"Thêm đúng 1 câu này, câu trả lời của ChatGPT khác một trời một vực."*

**Video Subject:**
```
Mẹo prompt giúp ChatGPT trả lời thông minh và chính xác hơn nhiều lần
```

**Video Script:**
```
Chỉ cần thêm đúng một câu này vào ChatGPT, câu trả lời sẽ khác một trời một vực. Câu thần chú đó là: hãy đóng vai một chuyên gia hàng đầu trong lĩnh vực này, và đặt cho tôi vài câu hỏi trước khi trả lời. Vì sao nó hiệu nghiệm? Thứ nhất, gán vai chuyên gia khiến AI dùng kiến thức chuyên sâu, thay vì trả lời chung chung nhạt nhẽo. Thứ hai, bắt nó hỏi lại buộc nó hiểu đúng nhu cầu của bạn, thay vì đoán mò. Kết quả là câu trả lời đúng trọng tâm và sâu sắc hơn hẳn. Một mẹo nữa: luôn yêu cầu nó giải thích từng bước. Cách bạn đặt câu hỏi quyết định chất lượng câu trả lời. Lưu câu thần chú này lại để dùng ngay nhé. Bạn muốn thêm vài prompt cực mạnh nữa không?
```

**Video Keywords:**
```
chatgpt prompt screen typing, person using laptop AI, chat conversation interface, expert thinking idea, glowing light bulb, smartphone AI app, coding text screen, technology productivity
```

- **Hashtag/Caption:** `#ChatGPT #prompt #AI #meohay #shorts`
- **Vì sao hot:** Bí kíp dùng được ngay + áp dụng cho hàng triệu người đang dùng ChatGPT → lưu/chia sẻ cao.
- **Biến thể A/B:** Test demo "trước/sau" (so sánh 2 câu trả lời) vs chỉ giải thích.

---

## 4. Nguyên tắc Hook & Retention (giữ cố định mọi video để A/B test công bằng)

1. **3 giây đầu là sống còn:** 50–60% người xem rớt trong 3s đầu. Mục tiêu **hook rate > 70%**.
2. **Hook mạnh = tuyên bố gây sốc + khoảng trống tò mò** ("bold claim + curiosity gap"). Tất cả 10 hook trên đều theo công thức này.
3. **Chữ to, đọc được khi tắt tiếng:** nhiều người xem không bật loa → phụ đề rõ là bắt buộc (xem Mục 0).
4. **Nhịp nhanh, không có đoạn "chết":** câu ngắn, vào thẳng vấn đề.
5. **Tạo vòng lặp / mời tương tác ở cuối:** câu hỏi hoặc "theo dõi xem phần 2" → tăng replay & comment (tín hiệu đẩy của thuật toán).
6. **Độ dài:** giữ ~40–55s cho cả 10 video để biến số duy nhất là *nội dung/ngách*.

---

## 5. Quy trình A/B TESTING

### 5.1 Thiết lập thí nghiệm (giữ MỌI thứ giống nhau trừ nội dung)
Để kết quả nói lên đúng "ngách nào ăn", **cố định**: độ dài (~40–55s), 1 giọng đọc, 1 font + style phụ đề, có BGM, cùng khung giờ đăng. **Biến số duy nhất = chủ đề/ngách.**

### 5.2 Lịch đăng
- **1 video/ngày trong 10 ngày**, đăng **xen kẽ ngách** (V1 facts → V3 tâm lý → V5 tiền → V7 bí ẩn → V9 AI → V2 → V4 → V6 → V8 → V10) để không ngách nào bị thiệt vì "ngày xấu".
- Khung giờ vàng VN: **19h–22h**.

### 5.3 Metric theo dõi (YouTube Studio → từng Short)
| Metric | Mục tiêu | Ý nghĩa |
|---|---|---|
| **% xem qua 3 giây** (hook rate) | > 70% | Hook có giữ chân không |
| **Average view % / Viewed vs swiped away** | càng cao càng tốt | Nội dung có "dính" không |
| **Views / lượt tiếp cận** | so sánh tương đối | Thuật toán có đẩy tiếp không |
| **(Like+Comment+Share) / Views** | > 5–8% | Mức độ cộng hưởng |
| **Subscribers mới / video** | so sánh | Có biến người xem thành fan không |

### 5.4 Tiêu chí chọn ngách thắng (sau 7–14 ngày kể từ video cuối)
Ngách thắng = ngách có **hook rate > 70%** VÀ tổng điểm cao nhất ở *retention + tỷ lệ tương tác + sub mới*. (Bỏ qua các video "ăn may" 1 lần — nhìn trung bình của cả ngách.)

### 5.5 Vòng lặp sau test
- **Ngách thắng:** chuyển sang chiến lược **Depth** — làm 10–20 video tiếp trong ngách đó, rồi A/B test biến thể *hook / tiêu đề / độ dài* (controlled test) để tối ưu sâu.
- **Ngách thua:** loại, hoặc thử lại với góc tiếp cận khác 1 lần trước khi bỏ.
- **Lưu ý thống kê:** 2 video/ngách chỉ là **tín hiệu sàng lọc vòng 1**, chưa phải kết luận chắc chắn. Coi đây là bước "khoanh vùng", không phải "chốt hạ".

---

## 6. Checklist nhanh trước khi đăng mỗi video

- [ ] Font phụ đề **KHÔNG** phải font Trung mặc định (dùng `DejaVuSans.ttf` hoặc `BeVietnamPro-Bold.ttf`).
- [ ] Tỉ lệ **Portrait 9:16 (1080×1920)**.
- [ ] Giọng **vi-VN**, đã nghe thử (kiểm tra đọc số/từ viết tắt cho tự nhiên).
- [ ] Phụ đề hiển thị **đủ dấu tiếng Việt**, không vỡ chữ.
- [ ] Xem lại 3 giây đầu: hook có "đập vào mặt" ngay không?
- [ ] Tiêu đề + 3–5 hashtag đúng ngách.
- [ ] Đăng đúng khung giờ vàng, ghi lại ngày/giờ để so sánh.

---

## 7. Bước tiếp theo gợi ý

1. Thêm font **Be Vietnam Pro Bold** vào `resource/fonts/` (hoặc dùng tạm `DejaVuSans.ttf`).
2. Gen thử **1 video** (gợi ý: V1 hoặc V9) → kiểm tra phụ đề/giọng/footage ổn → mới gen loạt.
3. Đăng theo lịch Mục 5.2, ghi số liệu vào một bảng tính.
4. Sau 2 tuần: chốt ngách thắng → quay lại tôi để lên **batch 10 video chuyên sâu** cho ngách đó.

---

## Nguồn research (xu hướng & RPM 2026)
- [OutlierKit — Most Profitable YouTube Niches](https://outlierkit.com/blog/most-profitable-youtube-niches)
- [Virvid — First 3 Seconds Hooks (Faceless Shorts)](https://virvid.ai/blog/first-3-seconds-hook-faceless-shorts-2026)
- [OpusClip — YouTube Shorts Hook Formulas](https://www.opus.pro/blog/youtube-shorts-hook-formulas)
- [Sadesign — YouTube Shorts 2026 (tiếng Việt)](https://sadesign.vn/youtube-shorts-2026-bi-quyet-tao-video-ngan-thu-hut-trieu-view)
- [Veefly — 30 Viral Shorts Ideas 2026](https://blog.veefly.com/youtube-marketing/30-viral-youtube-shorts-ideas-for-your-next-video-in-2026/)
