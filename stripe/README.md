# DreamCobots Stripe Integration

This directory contains Stripe payment library integrations for all DreamCobots bots,
organized by language/platform.

## Directory Structure

```
stripe/
├── node/        # Node.js — Payment Intents, webhooks (Express)
├── python/      # Python  — Payments, subscriptions, webhooks (Flask)
├── ruby/        # Ruby    — Checkout sessions, webhooks (Sinatra)
├── php/         # PHP     — Payment Intents, webhooks
├── go/          # Go      — Payment Intents, webhooks (net/http)
├── java/        # Java    — Payments, subscriptions (Maven)
├── dotnet/      # .NET    — Payments, subscriptions (ASP.NET Core)
├── ios/         # iOS/Swift — PaymentSheet (SwiftUI + CocoaPods)
└── android/     # Android/Kotlin — PaymentSheet (Jetpack Compose + Gradle)
```

## Environment Variables

Set these variables before running any integration:

| Variable                 | Description                                    |
|--------------------------|------------------------------------------------|
| `STRIPE_SECRET_KEY`      | Your Stripe secret key (`sk_live_...`)         |
| `STRIPE_PUBLISHABLE_KEY` | Your Stripe publishable key (`pk_live_...`)    |
| `STRIPE_WEBHOOK_SECRET`  | Webhook signing secret from the Stripe Dashboard |

> **Never commit real API keys.** Copy `.env.example` to `.env` and fill in your values.
> The `.gitignore` file already excludes `.env`.

```bash
cp .env.example .env
# Edit .env and add your keys
```

---

## Quick Start by Language

### Node.js

```bash
cd stripe/node
npm install
export STRIPE_SECRET_KEY=sk_...
node index.js
```

Test webhooks locally:
```bash
stripe listen --forward-to localhost:3000/webhook
```

### Python

```bash
cd stripe/python
pip install -r requirements.txt
export STRIPE_SECRET_KEY=sk_...
python app.py
```

Test webhooks locally:
```bash
stripe listen --forward-to localhost:5000/webhook
```

### Ruby

```bash
cd stripe/ruby
bundle install
export STRIPE_SECRET_KEY=sk_...
ruby app.rb
```

### PHP

```bash
cd stripe/php
composer install
export STRIPE_SECRET_KEY=sk_...
php -S localhost:8000 index.php
```

### Go

```bash
cd stripe/go
go mod tidy
export STRIPE_SECRET_KEY=sk_...
go run main.go
```

### Java

```bash
cd stripe/java
mvn compile exec:java -Dexec.mainClass="com.dreamcobots.stripe.StripeIntegration"
```

### .NET

```bash
cd stripe/dotnet
dotnet restore
export STRIPE_SECRET_KEY=sk_...
dotnet run
```

### iOS (Swift)

```bash
cd stripe/ios
pod install
# Open the generated .xcworkspace in Xcode
```

### Android (Kotlin)

```bash
cd stripe/android
./gradlew assembleDebug
```

---

## Key Events Handled

All integrations handle these Stripe webhook events:

| Event                            | Description                        |
|----------------------------------|------------------------------------|
| `payment_intent.succeeded`       | One-time payment was successful    |
| `checkout.session.completed`     | Checkout session finished          |
| `customer.subscription.created` | New subscription was created       |
| `customer.subscription.deleted` | Subscription was canceled         |

---

## Testing with Stripe CLI

1. Install the [Stripe CLI](https://stripe.com/docs/stripe-cli).
2. Login: `stripe login`
3. Forward events to your local server:
   ```bash
   stripe listen --forward-to localhost:<PORT>/webhook
   ```
4. Trigger a test event:
   ```bash
   stripe trigger payment_intent.succeeded
   ```
