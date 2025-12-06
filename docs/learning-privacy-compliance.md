# Learning System Privacy & Compliance Documentation

## Overview

This document provides comprehensive legal and compliance documentation for Mobius's meta-learning system with privacy controls. It is designed to support enterprise sales, legal review, and customer transparency.

**Version:** 1.0  
**Last Updated:** December 5, 2025  
**Applies To:** Mobius Phase 2 Learning System

---

## Table of Contents

1. [Data Processing Addendum](#data-processing-addendum)
2. [Learning Modes Comparison](#learning-modes-comparison)
3. [Privacy Impact Assessment](#privacy-impact-assessment)
4. [Right to Deletion Workflow](#right-to-deletion-workflow)
5. [Consent Flow Documentation](#consent-flow-documentation)

---

## Data Processing Addendum

### Mobius Learning System - Data Processing Addendum

**Effective Date:** December 5, 2025

This Data Processing Addendum ("DPA") forms part of the Mobius Service Agreement between Customer and Mobius ("Agreement") and governs the processing of Personal Data in connection with the Mobius Learning System.

#### 1. Definitions

- **Personal Data**: Any information relating to an identified or identifiable natural person
- **Processing**: Any operation performed on Personal Data
- **Data Controller**: The entity that determines the purposes and means of processing Personal Data
- **Data Processor**: The entity that processes Personal Data on behalf of the Data Controller

#### 2. Privacy Tiers

The Mobius Learning System offers three privacy tiers, each with distinct data processing characteristics:

##### 2.1 Private Mode (Default)

**Data Processing:**
- Customer feedback data is processed solely for Customer's benefit
- No data sharing with other organizations
- Complete data isolation between brands
- Pattern extraction limited to Customer's data only

**Data Ownership:**
- Customer retains full ownership of all learning data
- Customer can export data at any time (GDPR Article 20)
- Customer can delete data at any time (GDPR Article 17)

**Privacy Guarantees:**
- No cross-customer data access
- No aggregate statistics shared
- No industry pattern contribution

##### 2.2 Shared Mode (Opt-in Only)

**Data Processing:**
- Customer feedback data is aggregated with other customers in same industry cohort
- Aggregation uses differential privacy (Laplace mechanism)
- K-anonymity enforced (minimum 5 contributing brands)
- Individual brand data cannot be reverse-engineered

**Data Ownership:**
- Customer retains ownership of raw feedback data
- Aggregated patterns are jointly owned by contributing customers
- Customer can opt-out at any time
- Opting out stops future contributions but does not remove past contributions from aggregates

**Privacy Guarantees:**
- Differential privacy with ε = 10 (noise scale = 0.1)
- K-anonymity with k ≥ 5
- No individual brand traces in aggregated patterns
- Pattern contributor anonymization

##### 2.3 Off Mode

**Data Processing:**
- No automated learning or pattern extraction
- Feedback data collected but not processed
- Manual review and adjustment only

**Data Retention:**
- Feedback data retained for audit purposes
- No learning patterns generated or stored

#### 3. Data Subject Rights

Mobius supports all GDPR data subject rights:

**Right to Access (Article 15):**
- GET /v1/brands/{brand_id}/learning/settings
- GET /v1/brands/{brand_id}/learning/patterns
- GET /v1/brands/{brand_id}/learning/audit

**Right to Data Portability (Article 20):**
- POST /v1/brands/{brand_id}/learning/export
- Returns machine-readable JSON format

**Right to Erasure (Article 17):**
- DELETE /v1/brands/{brand_id}/learning/data
- Permanently deletes all learning patterns
- Audit log retained for compliance

**Right to Rectification (Article 16):**
- Supported through pattern re-extraction after feedback correction

**Right to Restriction (Article 18):**
- Supported by setting privacy_tier to "off"

**Right to Object (Article 21):**
- Supported by opting out of shared learning

#### 4. Security Measures

**Technical Measures:**
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Access controls and authentication
- Audit logging of all data access

**Organizational Measures:**
- Regular security audits
- Employee training on data protection
- Incident response procedures
- Data breach notification within 72 hours

#### 5. Sub-processors

Mobius uses the following sub-processors:

- **Supabase**: Database and storage (PostgreSQL + Storage)
- **Modal**: Serverless compute infrastructure
- **Google Cloud**: AI/ML services (Gemini)

All sub-processors are GDPR-compliant and have executed Data Processing Agreements.

#### 6. Data Retention

- **Learning Patterns**: Retained according to Customer's data_retention_days setting (default: 365 days)
- **Audit Logs**: Retained for 7 years for compliance purposes
- **Feedback Data**: Retained according to Customer's retention policy

#### 7. Customer Obligations

Customer agrees to:
- Obtain necessary consents from end users
- Provide privacy notices to end users
- Respond to data subject requests
- Notify Mobius of any data breaches

#### 8. Liability and Indemnification

Mobius shall indemnify Customer against claims arising from Mobius's breach of this DPA, subject to the limitations in the Agreement.

---

## Learning Modes Comparison

### Quick Reference Chart

| Feature | Off Mode | Private Mode | Shared Mode |
|---------|----------|--------------|-------------|
| **Learning** | Disabled | Enabled | Enabled |
| **Data Scope** | N/A | Your brand only | Industry cohort |
| **Data Sharing** | None | None | Anonymized aggregates |
| **Privacy Guarantee** | Maximum | Complete isolation | K-anonymity + Differential privacy |
| **Network Effects** | No | No | Yes |
| **Compliance Score Improvement** | Manual only | Brand-specific | Industry-wide insights |
| **Suitable For** | Highly regulated industries | Most organizations | Organizations wanting network effects |
| **Default** | No | **Yes** | No (opt-in required) |

### Detailed Comparison

#### Off Mode

**When to Use:**
- Highly regulated industries (healthcare, finance)
- Organizations with strict data processing restrictions
- During initial evaluation period

**Benefits:**
- Maximum privacy
- No automated data processing
- Full manual control

**Limitations:**
- No automated improvements
- Manual review required for all changes
- No compliance score optimization

#### Private Mode (Recommended)

**When to Use:**
- Most organizations
- Default for all new brands
- Organizations wanting learning without data sharing

**Benefits:**
- Automated learning from your feedback
- Brand-specific prompt optimization
- Complete data isolation
- Full data ownership and control

**Limitations:**
- Limited to your brand's data
- No industry-wide insights
- Requires sufficient feedback volume (50+ events)

#### Shared Mode

**When to Use:**
- Organizations wanting network effects
- Brands in established industry cohorts
- Organizations comfortable with anonymized data sharing

**Benefits:**
- Learn from industry-wide patterns
- Faster improvement with less data
- Network effects from other brands
- Industry benchmarking

**Limitations:**
- Requires opt-in consent
- Minimum 5 brands in cohort
- Cannot remove past contributions after opting out

---

## Privacy Impact Assessment

### Executive Summary

The Mobius Learning System has been designed with privacy-first principles. This Privacy Impact Assessment (PIA) evaluates the privacy risks and mitigation measures.

**Assessment Date:** December 5, 2025  
**Assessor:** Mobius Privacy Team  
**Scope:** Learning System with Privacy Controls

### Risk Assessment

#### Risk 1: Individual Brand Identification in Shared Mode

**Risk Level:** Medium (before mitigation) → Low (after mitigation)

**Mitigation Measures:**
- K-anonymity enforcement (minimum 5 brands)
- Differential privacy noise injection
- Pattern contributor anonymization
- Aggregate-only storage

**Residual Risk:** Low

#### Risk 2: Data Breach

**Risk Level:** Medium (before mitigation) → Low (after mitigation)

**Mitigation Measures:**
- Encryption at rest and in transit
- Access controls and authentication
- Regular security audits
- Incident response procedures

**Residual Risk:** Low

#### Risk 3: Unauthorized Data Access

**Risk Level:** Medium (before mitigation) → Low (after mitigation)

**Mitigation Measures:**
- Role-based access control
- Audit logging of all access
- Multi-factor authentication
- Regular access reviews

**Residual Risk:** Low

### Privacy by Design Principles

1. **Proactive not Reactive**: Privacy controls built into system design
2. **Privacy as Default**: Private mode is the default setting
3. **Privacy Embedded**: Privacy controls integrated into all features
4. **Full Functionality**: Privacy doesn't compromise functionality
5. **End-to-End Security**: Security throughout data lifecycle
6. **Visibility and Transparency**: Full transparency dashboard
7. **Respect for User Privacy**: User control over all settings

### Compliance Assessment

- **GDPR**: Fully compliant
- **CCPA**: Fully compliant
- **HIPAA**: Compatible (with Off mode)
- **SOC 2**: Audit in progress

---

## Right to Deletion Workflow

### Overview

This document describes the complete workflow for exercising the right to deletion (GDPR Article 17) in the Mobius Learning System.

### User-Initiated Deletion

#### Step 1: Access Dashboard

User navigates to: Settings > Learning Privacy > Dashboard

#### Step 2: Initiate Deletion

User clicks "Delete Learning Data" button

**Warning Displayed:**
```
⚠️ Warning: This action cannot be undone

Deleting your learning data will permanently remove:
- All learned patterns
- Pattern extraction history
- Learning optimizations

This will NOT delete:
- Your feedback data (retained for audit)
- Audit log (retained for compliance)

Are you sure you want to proceed?

[Cancel] [Yes, Delete Permanently]
```

#### Step 3: Confirmation

User confirms deletion by:
1. Checking "I understand this action is permanent"
2. Clicking "Yes, Delete Permanently"

#### Step 4: API Request

System sends: `DELETE /v1/brands/{brand_id}/learning/data`

#### Step 5: Deletion Process

Backend performs:
1. Log deletion initiation to audit log
2. Delete all records from `brand_patterns` table
3. Verify deletion completed
4. Return confirmation

#### Step 6: Confirmation

User sees:
```
✓ Learning Data Deleted

All learning data has been permanently deleted.

Audit log entry created: [timestamp]

You can re-enable learning at any time from Settings.

[Return to Dashboard]
```

### API-Initiated Deletion

For programmatic deletion:

```bash
curl -X DELETE \
  https://api.mobius.com/v1/brands/{brand_id}/learning/data \
  -H "Authorization: Bearer {token}"
```

Response:
```json
{
  "brand_id": "brand-123",
  "deleted": true,
  "message": "All learning data has been permanently deleted",
  "request_id": "req_abc123"
}
```

### Verification

After deletion, verify by:

```bash
curl https://api.mobius.com/v1/brands/{brand_id}/learning/patterns \
  -H "Authorization: Bearer {token}"
```

Should return:
```json
{
  "brand_id": "brand-123",
  "patterns": [],
  "total": 0,
  "request_id": "req_def456"
}
```

### Audit Trail

All deletions are logged:

```bash
curl https://api.mobius.com/v1/brands/{brand_id}/learning/audit \
  -H "Authorization: Bearer {token}"
```

Returns:
```json
{
  "brand_id": "brand-123",
  "entries": [
    {
      "log_id": "log-789",
      "action": "data_deletion_initiated",
      "details": {
        "timestamp": "2025-12-05T10:30:00Z"
      },
      "timestamp": "2025-12-05T10:30:00Z"
    }
  ],
  "total": 1,
  "request_id": "req_ghi789"
}
```

---

## Consent Flow Documentation

### Overview

This document describes the complete consent flow for the Mobius Learning System, including UI mockups and implementation guidance.

### Initial Setup Flow

#### Screen 1: Privacy Tier Selection

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  Choose Your Learning Privacy Level                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ○ Off - Manual Only                                    │
│    No automated learning. Best for highly regulated     │
│    industries.                                          │
│                                                          │
│  ● Private - Your Brand Only (Recommended)              │
│    Learn from your brand's feedback only. Complete      │
│    data isolation. No sharing with other brands.        │
│                                                          │
│  ○ Shared - Industry Insights                           │
│    Contribute to anonymized industry patterns.          │
│    K-anonymity + Differential privacy protection.       │
│                                                          │
│  [Learn More About Privacy Tiers]                       │
│                                                          │
│                              [Cancel]  [Continue]        │
└─────────────────────────────────────────────────────────┘
```

#### Screen 2: Shared Mode Details (if selected)

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  Shared Learning Privacy Guarantees                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  How Your Data is Protected:                            │
│                                                          │
│  1. K-Anonymity (Minimum 5 Brands)                      │
│     Your data is only aggregated when at least 5        │
│     brands contribute. Individual brands cannot be      │
│     identified.                                         │
│                                                          │
│  2. Differential Privacy                                │
│     Random noise is added to prevent individual         │
│     brand identification, even with multiple queries.   │
│                                                          │
│  3. Aggregate-Only Storage                              │
│     Only aggregated patterns are stored. No             │
│     individual brand traces remain.                     │
│                                                          │
│  What IS Shared:                                        │
│  ✓ "Fashion brands prefer warm colors" (aggregate)     │
│                                                          │
│  What IS NOT Shared:                                    │
│  ✗ "Brand X uses #FF0000" (individual data)            │
│                                                          │
│                              [Back]  [Continue]          │
└─────────────────────────────────────────────────────────┘
```

#### Screen 3: Consent Confirmation

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  Confirm Your Choice                                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  You selected: Private Learning                         │
│                                                          │
│  This means:                                            │
│  • Learning from your brand's feedback only             │
│  • Complete data isolation                              │
│  • No data sharing with other brands                    │
│  • You can change this anytime                          │
│                                                          │
│  ☐ I understand how my data will be used               │
│  ☐ I consent to Private learning mode                  │
│                                                          │
│  [View Full Privacy Policy]                             │
│  [View Data Processing Addendum]                        │
│                                                          │
│                              [Back]  [Confirm]           │
└─────────────────────────────────────────────────────────┘
```

#### Screen 4: Confirmation & Next Steps

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  ✓ Learning Privacy Settings Saved                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Your privacy tier: Private                             │
│  Consent date: December 5, 2025                         │
│                                                          │
│  Next Steps:                                            │
│  • View your learning dashboard                         │
│  • Export your learning data anytime                    │
│  • Change settings anytime                              │
│                                                          │
│  [View Dashboard]  [Go to Settings]                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Changing Privacy Tier

**Flow:**
1. Navigate to Settings > Learning Privacy
2. View current tier and consent date
3. Click "Change Privacy Tier"
4. Follow screens 1-4 above
5. If downgrading from Shared to Private:
   - Show warning: "Your past contributions will remain in industry patterns, but no new data will be shared"
6. If upgrading to Shared:
   - Full consent flow required (screens 2-3)

### Implementation Notes

**Required Fields:**
- `privacy_tier`: "off" | "private" | "shared"
- `consent_date`: ISO 8601 timestamp
- `consent_version`: "1.0"

**API Endpoint:**
```
POST /v1/brands/{brand_id}/learning/settings
{
  "privacy_tier": "private",
  "consent_date": "2025-12-05T10:30:00Z"
}
```

**Validation:**
- Consent required for any tier except "off"
- Consent date must be current or recent (within 24 hours)
- Consent version must match current version

---

## Appendix: Frequently Asked Questions

### For Customers

**Q: What happens to my data if I switch from Shared to Private mode?**  
A: Your past contributions remain in industry patterns (they cannot be removed without affecting other brands), but no new data will be shared. All future learning will be private to your brand only.

**Q: Can I delete my learning data?**  
A: Yes, you can delete all learning patterns at any time via the dashboard or API. This action is permanent and cannot be undone.

**Q: How long does it take for learning to improve my compliance scores?**  
A: In Private mode, you'll see improvements after 50+ feedback events. In Shared mode, improvements can be faster due to industry-wide patterns.

### For Legal Teams

**Q: Is the system GDPR compliant?**  
A: Yes, the system is fully GDPR compliant, supporting all data subject rights including access, portability, erasure, and objection.

**Q: What is the legal basis for processing?**  
A: Legitimate interest for Private mode (improving customer's own service), and explicit consent for Shared mode.

**Q: Are sub-processors GDPR compliant?**  
A: Yes, all sub-processors (Supabase, Modal, Google Cloud) are GDPR compliant and have executed Data Processing Agreements.

### For Sales Teams

**Q: How do I explain the privacy tiers to customers?**  
A: Use the comparison chart above. Emphasize that Private mode (default) provides learning benefits without any data sharing, while Shared mode offers network effects with strong privacy guarantees.

**Q: What if a customer is in a highly regulated industry?**  
A: Recommend Off mode for maximum privacy, or Private mode if they want learning benefits without data sharing.

**Q: Can customers switch tiers later?**  
A: Yes, customers can change their privacy tier at any time through the dashboard or API.

---

## Document Control

**Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-12-05 | Initial release | Mobius Privacy Team |

**Review Schedule:**
- Quarterly review by Legal team
- Annual review by Privacy team
- Ad-hoc review for regulatory changes

**Contact:**
- Privacy questions: privacy@mobius.com
- Legal questions: legal@mobius.com
- Technical questions: support@mobius.com
