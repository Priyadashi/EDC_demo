# EDC Demo Presentation Script

Use this script to demonstrate sovereign data exchange using the Automotive EDC Demo.

**Duration**: 15-20 minutes
**Audience**: Business stakeholders, technical teams, automotive industry professionals

---

## Pre-Demo Checklist

- [ ] Demo UI is accessible and both connectors show "Online"
- [ ] Browser is in presentation mode (hide bookmarks, increase font size)
- [ ] Demo has been reset (click "Reset Demo" button)

---

## Part 1: Introduction (3 minutes)

### Opening Statement

> "Today I'll demonstrate how automotive companies can securely exchange data while maintaining complete control over their information. This is based on the Eclipse Dataspace Connector principles used by Catena-X, the automotive industry's data ecosystem."

### The Challenge

> "In the automotive industry, companies need to share data with partners - parts catalogs with suppliers, quality metrics with manufacturers, traceability data for compliance. But traditional data sharing has problems:
> - Once you share data, you lose control
> - There's no standard way to enforce usage policies
> - Auditing who accessed what is difficult
> - Each partner relationship requires custom integration"

### The Solution

> "Eclipse Dataspace Connector, or EDC, solves these problems by:
> - Requiring contracts before any data transfer
> - Enforcing policies automatically
> - Providing complete audit trails
> - Using standardized protocols for interoperability"

---

## Part 2: Architecture Overview (2 minutes)

### Show the Overview Tab

> "Let me show you our demo architecture. We have two connectors:

> **On the left is the Provider** - This represents an automotive OEM like BMW or Volkswagen. They have data assets they want to share with their supply chain.

> **On the right is the Consumer** - This represents a Tier-1 supplier like Bosch or Continental. They need access to the OEM's data to do their job.

> **In the middle is the Dataspace Protocol** - This standardized protocol ensures both parties can communicate regardless of their internal systems."

### Point Out Key Features

> "Notice a few things:
> - Both connectors have APIs for catalog, negotiation, and transfer
> - The consumer has an 'identity' with attributes like certifications
> - Data only flows after a contract is agreed"

---

## Part 3: Browsing the Catalog (3 minutes)

### Fetch the Catalog

> "Let's start as the Tier-1 supplier. First, we need to see what data the OEM is offering."

**Action**: Click "Fetch Catalog" button

> "The consumer connector reaches out to the provider and retrieves their data catalog. This uses the Dataspace Protocol's Catalog Request."

### Show Available Datasets

> "We can see three datasets:
> 1. **2024 Vehicle Part Catalog** - Complete parts information for electric vehicles
> 2. **Q4 2024 Quality Metrics** - Supplier performance data
> 3. **Battery Traceability Data** - For regulatory compliance like the EU Battery Regulation"

### Explain Policies

**Action**: Click on one of the datasets

> "Each dataset has a policy attached. Look at this one - it says 'Allows USE when partner_type equals tier1_supplier'. This means only certified Tier-1 suppliers can access this data. The policy is machine-readable and will be enforced automatically."

---

## Part 4: Contract Negotiation (5 minutes)

### Start Negotiation

**Action**: Click "Request Access (Start Negotiation)"

> "Now we're initiating a contract negotiation. This is where EDC really shines. Watch the state machine progress..."

### Explain the Steps

> "The negotiation follows a formal protocol:
> 1. **REQUESTED** - Consumer asks for access
> 2. **OFFERED** - Provider evaluates and makes an offer
> 3. **AGREED** - Consumer accepts the terms
> 4. **VERIFIED** - Both parties verify the agreement
> 5. **FINALIZED** - Contract is now active"

### Show Policy Evaluation

**Action**: Click "Request Provider Offer"

> "The provider is now evaluating our identity against the policy. We said we're a Tier-1 supplier with TISAX and ISO27001 certifications..."

**Wait for result**

> "The policy evaluation passed! Look at the constraints that were checked:
> - partner_type = tier1_supplier ✓
>
> This is automatic, machine-enforced access control."

### Complete Negotiation

**Action**: Click through Agree → Verify → Finalize

> "With each step, both parties move closer to a binding agreement. This creates a complete audit trail."

**After Finalize**:

> "We now have a Contract Agreement with a unique ID. This agreement authorizes us to receive the data. Without it, the transfer would be rejected."

---

## Part 5: Data Transfer (3 minutes)

### Initiate Transfer

**Action**: Go to Transfer tab, click "Initiate Data Transfer"

> "With our contract in place, we can now request the actual data. The provider will verify our agreement before sending anything."

### Execute Transfer

**Action**: Click "Start Transfer" then "Complete & Receive Data"

> "Watch the data flow animation - this represents the actual data movement from the provider to the consumer. In production, this could be large datasets, streaming data, or file transfers."

### Show Completion

> "Transfer complete! The data is now in our consumer's data store, and we have:
> - Full audit trail of how we got it
> - The contract governing our usage
> - The policy we agreed to follow"

---

## Part 6: Viewing the Data (2 minutes)

### Show Data Tab

**Action**: Go to Data tab

> "Here's the actual data we received. This is real automotive data - a complete parts catalog with specifications, supplier information, and vehicle applicability."

### Expand Sections

**Action**: Expand the catalog section

> "Look at the detail - part numbers, specifications like motor power and torque, which vehicle models they apply to. This is the kind of data that flows through Catena-X every day."

### Highlight Governance

> "But here's the important part - this data came with strings attached. The contract we signed prohibits us from distributing this to third parties. In a real EDC deployment, usage policies would be continuously enforced."

---

## Part 7: Key Takeaways (2 minutes)

### Summarize Benefits

> "What we just saw demonstrates several key principles:

> **1. Data Sovereignty** - The OEM maintains control over their data through policies and contracts. They decide who can access what.

> **2. Contract-Based Exchange** - Every data transfer requires a negotiated contract. No contract, no data.

> **3. Automated Policy Enforcement** - Policies are checked automatically. We couldn't have accessed this data if we weren't a certified Tier-1 supplier.

> **4. Complete Auditability** - Every step is logged. Who requested what, when, and what was the outcome.

> **5. Interoperability** - Using standardized protocols, any company can participate regardless of their internal systems."

### Connect to Real World

> "This is exactly what's happening in Catena-X today. Hundreds of automotive companies are using this approach to share data securely across their supply chains."

---

## Part 8: Q&A Prompts

Common questions and suggested answers:

### "How is this different from an API?"

> "With a normal API, once you have credentials, you can access data freely. With EDC, each data access requires a new contract negotiation. Policies can change, access can be revoked, and everything is tracked."

### "What about performance?"

> "Contract negotiation adds overhead, but it's typically done once per data relationship. Once you have an agreement, transfers can be very fast. The negotiation usually takes seconds."

### "Can policies be more complex?"

> "Absolutely. Policies can include time restrictions (expires December 31), purpose limitations (only for quality analysis), geographic constraints (EU only), and much more."

### "What if someone violates the policy?"

> "In this demo, policies are informational after transfer. In production EDC deployments, usage enforcement can be integrated with logging, monitoring, and even DRM-like controls."

---

## Demo Reset

After the demo, click "Reset Demo" to clear all negotiations and transfers for the next presentation.

---

## Backup: Showing Policy Failure

To demonstrate policy enforcement, you can modify the consumer's identity:

1. Use the Consumer API at `/api/identity`
2. Change `partner_type` to `unauthorized`
3. Try to negotiate - it will be terminated with "Policy requirements not met"

This powerfully demonstrates that access control is real.
