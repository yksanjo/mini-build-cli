# 📋 AuditLog.io

> **SOC2-compliant audit logging for SaaS teams**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue)](https://www.typescriptlang.org/)
[![SOC2](https://img.shields.io/badge/compliance-SOC2-green)](https://)

Drop-in audit logging for compliance. Immutable, tamper-proof, audit-ready.

## 😤 The Problem

SOC2 requires audit logs:
- Who accessed what data when?
- What changes were made?
- Can you prove it wasn't tampered with?

Building this from scratch takes weeks. Compliance auditors demand it.

## ✨ Features

- **🔒 Immutable Logs** - Cryptographically tamper-proof
- **🔐 Audit Trail** - Complete user activity history
- **📊 Compliance Dashboard** - SOC2, GDPR ready
- **⚡ Real-time Streaming** - Live audit events
- **📤 Export** - Auditor-friendly reports
- **🔍 Search** - Query across millions of events
- **🚨 Alerts** - Anomaly detection

## 💰 Pricing

| Plan | Price | Includes |
|------|-------|----------|
| **Self-Hosted** | Free | Unlimited logs |
| **Starter** | $49/mo | 100K events, 30-day retention |
| **Pro** | $149/mo | 1M events, 1-year retention |
| **Enterprise** | $499/mo | Unlimited, 7-year retention |

**Compliance is expensive. We make it affordable.**

## 🚀 Quick Start

### Installation

```bash
npm install @auditlog/sdk
```

### Basic Usage

```javascript
import { AuditLog } from '@auditlog/sdk';

const audit = new AuditLog({
  apiKey: 'your-api-key',
  service: 'my-saas-app'
});

// Log an event
await audit.log({
  actor: {
    id: 'user-123',
    type: 'user',
    email: 'admin@company.com'
  },
  action: 'user.created',
  target: {
    id: 'user-456',
    type: 'user'
  },
  metadata: {
    ip: '192.168.1.1',
    userAgent: 'Mozilla/5.0...'
  }
});
```

## 🎯 Example: User Login

```javascript
app.post('/login', async (req, res) => {
  const user = await authenticate(req.body);
  
  if (user) {
    await audit.log({
      actor: { id: user.id, type: 'user' },
      action: 'auth.login.success',
      target: { id: user.id, type: 'user' },
      metadata: {
        ip: req.ip,
        userAgent: req.headers['user-agent'],
        method: 'password'
      }
    });
    
    res.json({ success: true });
  } else {
    await audit.log({
      actor: { id: req.body.email, type: 'email' },
      action: 'auth.login.failed',
      metadata: {
        ip: req.ip,
        reason: 'invalid_credentials'
      }
    });
    
    res.status(401).json({ error: 'Invalid credentials' });
  }
});
```

## 📊 Compliance Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  AuditLog.io Dashboard                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📈 Events (24h)             🔒 Tamper Status               │
│  ┌─────────┐                 ┌─────────┐                   │
│  │  23,456 │                 │   ✅ OK   │                   │
│  │  +5%    │                 │ 0 issues  │                   │
│  └─────────┘                 └─────────┘                   │
│                                                             │
│  🚨 Security Alerts                                         │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ ⚠️  Multiple failed logins │ user-123 │ 5m ago        │ │
│  │ ⚠️  Data export attempted  │ admin-5  │ 12m ago       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  📋 Recent Audit Events                                     │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Time │ Actor    │ Action        │ Target │ Status    │ │
│  │ 2s   │ user-123 │ user.updated  │ user-456│ ✅ Success│ │
│  │ 5s   │ admin-5  │ data.export   │ export-1│ ✅ Success│ │
│  │ 10s  │ user-789 │ auth.login    │ user-789│ ❌ Failed │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔒 Immutable Logs

```javascript
// Every log entry is cryptographically signed
const entry = await audit.log({
  actor: { id: 'user-123', type: 'user' },
  action: 'data.export',
  target: { id: 'export-456', type: 'export' }
});

// Entry includes:
// {
//   id: 'evt_abc123',
//   timestamp: '2024-01-15T10:30:00Z',
//   hash: 'sha256:abcdef...',
//   signature: 'sig_xyz789...',
//   previousHash: 'sha256:123456...'  // Links to previous entry
// }
```

**Tamper Detection:**
```javascript
// Verify log integrity
const isValid = await audit.verifyChain();
// Returns: true if all entries are valid
//          false if any entry was tampered with
```

## 🎯 Automatic Middleware

### Express
```javascript
import { auditMiddleware } from '@auditlog/sdk-express';

app.use(auditMiddleware({
  audit,
  // Auto-log all requests
  logRequests: true,
  // Log specific actions
  actions: {
    'POST /api/users': 'user.created',
    'PUT /api/users/:id': 'user.updated',
    'DELETE /api/users/:id': 'user.deleted'
  }
}));
```

### Database Triggers
```javascript
import { auditPrisma } from '@auditlog/sdk-prisma';

const prisma = new PrismaClient();
prisma.$use(auditPrisma({
  audit,
  models: {
    User: ['create', 'update', 'delete'],
    Organization: ['create', 'update', 'delete']
  }
}));
```

## 🔍 Search & Query

```javascript
// Search by actor
const events = await audit.query({
  actor: { id: 'user-123' },
  from: '2024-01-01',
  to: '2024-01-31'
});

// Search by action
const logins = await audit.query({
  action: 'auth.login.success',
  from: '2024-01-01'
});

// Search by target
const userChanges = await audit.query({
  target: { id: 'user-456', type: 'user' }
});

// Complex query
const suspicious = await audit.query({
  action: 'auth.login.failed',
  from: '2024-01-15',
  metadata: {
    ip: '192.168.1.100'
  },
  count: { $gte: 5 }  // 5+ failed attempts
});
```

## 🚨 Anomaly Detection

```javascript
// Configure alerts
audit.on('anomaly', async (alert) => {
  // Send to Slack, PagerDuty, etc.
  await slack.send({
    channel: '#security',
    text: `🚨 ${alert.type}: ${alert.description}`
  });
});

// Built-in detectors:
// - Multiple failed logins
// - Unusual data access patterns
// - Privilege escalation attempts
// - Off-hours admin activity
// - Bulk data exports
```

## 📤 Auditor Reports

```javascript
// Generate SOC2 report
const report = await audit.export({
  format: 'pdf', // or 'csv', 'json'
  from: '2024-01-01',
  to: '2024-01-31',
  filters: {
    actions: ['user.login', 'data.access', 'data.export']
  }
});

// Tamper-proof certificate
const certificate = await audit.generateCertificate({
  from: '2024-01-01',
  to: '2024-01-31'
});
// Returns signed document proving log integrity
```

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Your App  │────▶│  AuditLog.io │────▶│   Kafka     │
│             │     │     SDK      │     │   Queue     │
└─────────────┘     └──────────────┘     └─────────────┘
                                                  │
                    ┌─────────────────────────────┘
                    ▼
         ┌─────────────────────┐
         │   Log Processors    │
         │                     │
         │  • Normalization    │
         │  • Enrichment       │
         │  • Hashing          │
         └─────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌─────────┐  ┌──────────┐  ┌──────────┐
│ClickHouse│  │   S3     │  │  Glacier │
│ (Hot)   │  │ (Warm)   │  │  (Cold)  │
│ 30 days │  │ 1 year   │  │ 7 years  │
└─────────┘  └──────────┘  └──────────┘
```

## 🛠️ Tech Stack

- **SDK:** TypeScript
- **Queue:** Kafka / Redis Streams
- **Hot Storage:** ClickHouse
- **Cold Storage:** S3 / Glacier
- **Dashboard:** Next.js, Tailwind
- **Crypto:** Node.js crypto, SHA-256

## 📁 Project Structure

```
audit-logs-compliance/
├── apps/
│   ├── api/                    # Ingestion API
│   ├── dashboard/              # Compliance dashboard
│   └── verifier/               # Log integrity verifier
├── packages/
│   ├── sdk-node/               # Node.js SDK
│   ├── sdk-python/             # Python SDK
│   ├── sdk-go/                 # Go SDK
│   ├── prisma/                 # Prisma integration
│   └── shared/                 # Shared types
├── docs/
└── infra/
    └── docker-compose.yml
```

## 🚀 Deployment

### Cloud
```bash
# Sign up at auditlog.io
npm install @auditlog/sdk
```

### Self-Hosted
```bash
git clone https://github.com/yourusername/audit-logs-compliance.git
cd audit-logs-compliance
docker-compose up -d
```

## 📚 Compliance Standards

### SOC2 Type II
- ✅ User access logging
- ✅ Data modification tracking
- ✅ Administrative actions
- ✅ Failed access attempts
- ✅ Tamper-proof evidence

### GDPR
- ✅ Data access logging
- ✅ Consent tracking
- ✅ Right to erasure audit
- ✅ Data export audit

### HIPAA
- ✅ PHI access logging
- ✅ User authentication
- ✅ Data modification tracking

## 🔐 Security

- ✅ End-to-end encryption
- ✅ Cryptographic signatures
- ✅ Immutable storage (WORM)
- ✅ Access controls
- ✅ Audit of audit system (meta-audit)

## 📈 Performance

| Metric | Value |
|--------|-------|
| Ingestion latency | < 10ms |
| Query latency | < 100ms |
| Retention | 7 years |
| Availability | 99.99% |

## 🤝 Comparison

| Feature | AuditLog.io | DIY | AuditBoard |
|---------|-------------|-----|------------|
| Drop-in SDK | ✅ | ❌ | ❌ |
| Immutable logs | ✅ | ⚠️ | ✅ |
| SOC2 templates | ✅ | ❌ | ✅ |
| Flat pricing | ✅ | ✅ | ❌ |
| Open source | ✅ | ✅ | ❌ |

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🌟 Why AuditLog.io?

Because compliance shouldn't require a dedicated team.

- **Drop-in** - SDK takes 10 minutes to integrate
- **Immutable** - Tamper-proof by design
- **Audit-ready** - Export SOC2 reports instantly
- **Affordable** - Fraction of enterprise tools

---

[Documentation](https://auditlog.io) • [SOC2 Guide](https://docs.auditlog.io/soc2) • [Discord](https://discord.gg/auditlog)
