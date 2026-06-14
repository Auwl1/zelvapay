# ZelvaPay 🚀
### Nigeria's Premium Digital Finance Platform

A complete, production-ready frontend for a VTU/fintech platform. Premium dark UI built with pure HTML, CSS, and JavaScript — no frameworks, no dependencies, zero build step.

---

## 📁 Project Structure

```
zelvapay/
├── index.html              ← Landing page
├── css/
│   └── main.css            ← Full design system (~900 lines)
├── js/
│   └── main.js             ← Utility functions & interactions
└── pages/
    ├── dashboard.html      ← Main dashboard
    ├── data.html           ← Buy data bundles
    ├── airtime.html        ← Buy airtime + airtime-to-cash
    ├── electricity.html    ← Electricity tokens (all DISCOs)
    ├── cable.html          ← Cable TV (DSTv/GOtv/Startimes)
    ├── virtual-card.html   ← USD & Naira virtual cards
    ├── giftcard.html       ← 50+ gift card brands
    ├── transfer.html       ← Bank transfer
    ├── transactions.html   ← Full transaction history
    ├── fund-wallet.html    ← Fund wallet (bank/card/USSD)
    ├── api-settings.html   ← API keys + provider integrations
    ├── exam.html           ← WAEC/NECO/NABTEB pins
    └── login.html          ← Sign in / Register
```

---

## 🔌 API Providers Supported

Configure all providers under **API Settings**:

| Provider      | Purpose                        |
|---------------|-------------------------------|
| Monnify       | Wallet funding (bank transfer) |
| Paystack      | Card payments                  |
| GSUBZ         | Data bundles                   |
| SMEPlug       | Data & airtime                 |
| VTPass        | Electricity, cable, exam       |
| AutopilotNG   | Data vending                   |
| OGDAMS        | Data vending                   |
| GeoDNATech    | Data vending                   |
| DataMall      | Data vending                   |
| Sudo Africa   | Virtual card issuance          |

---

## 🛠 Backend Integration (Django)

Connect this frontend to your Django backend:

### 1. Data Purchase
```python
# views.py — POST /api/data/
def buy_data(request):
    network = request.POST.get('network')    # MTN, Airtel, Glo, 9Mobile
    phone   = request.POST.get('phone')
    plan_id = request.POST.get('plan_id')   # e.g. mtn_1gb
    # → call GSUBZ / SMEPlug / AUTOPILOTNG API
```

### 2. Wallet Funding (Monnify Webhook)
```python
# views.py — POST /monnify/webhook/
def monnify_payment_done(request):
    config = WebsiteConfiguration.objects.first()
    # Verify HMAC hash → credit user wallet
```

### 3. Virtual Cards (Sudo Africa)
```python
# POST /api/virtual-card/create/
# Headers: Authorization: Bearer {SUDO_API_KEY}
# Body: { currency: "USD", type: "virtual", brand: "visa" }
```

---

## 🚀 Deploy to GitHub Pages

```bash
git init
git add .
git commit -m "Initial ZelvaPay frontend"
git remote add origin https://github.com/YOUR_USERNAME/zelvapay.git
git push -u origin main
```

Then go to **Settings → Pages → Branch: main → / (root)** → Save.

Your site will be live at: `https://your-username.github.io/zelvapay/`

---

## 🎨 Design System

| Token       | Value    | Usage              |
|-------------|----------|--------------------|
| `--bg`      | `#060810`| Page background    |
| `--accent`  | `#6C63FF`| Primary/buttons    |
| `--green`   | `#22D3A5`| Success/credit     |
| `--orange`  | `#F97316`| Warning/pending    |
| `--red`     | `#F87171`| Error/debit        |
| `--blue`    | `#38BDF8`| Info/secondary     |

Fonts: **Syne** (display) · **Inter** (body) · **JetBrains Mono** (numbers/code)

---

## 📞 Support

Built for AjosData / ZelvaPay by Muhammad Auwal.
