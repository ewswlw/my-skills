# Domain-Specific Question Templates

When detecting a project archetype in Phase 1, inject these specific questions into your dynamically generated interview categories.

## 1. SaaS / B2B Application
- **Multi-tenancy:** "How strict must data isolation be between tenants? a) Logical separation (tenant_id column) [RECOMMENDED], b) Schema per tenant, c) Database per tenant."
- **Authentication:** "What SSO providers are required for enterprise customers? a) Just email/Google [RECOMMENDED], b) SAML/Okta integration, c) Active Directory."
- **Billing:** "How will you handle metered billing or usage limits? a) Stripe/Paddle integration [RECOMMENDED], b) Custom internal ledger, c) No metered billing needed."
- **Roles:** "How complex is the RBAC (Role-Based Access Control)? a) Admin/User only [RECOMMENDED], b) Custom roles with granular permissions, c) Hierarchical org structures."

## 2. E-Commerce Platform
- **Inventory:** "How will inventory sync with external systems (e.g., Shopify, ERP)? a) Webhooks on order completion [RECOMMENDED], b) Scheduled batch sync, c) No external sync."
- **Payments:** "How do you handle split payments or marketplace payouts? a) Stripe Connect [RECOMMENDED], b) Manual payouts, c) Standard single-vendor checkout."
- **Tax/Compliance:** "Who calculates sales tax/VAT at checkout? a) TaxJar/Stripe Tax [RECOMMENDED], b) Custom rules engine, c) Flat rate."

## 3. Data Pipeline / ETL
- **Idempotency:** "If a job fails halfway, how does it recover? a) Drop partition and rerun full batch [RECOMMENDED], b) Upsert/merge on primary key, c) Manual intervention required."
- **Backfilling:** "How do you handle historical data backfills when logic changes? a) Parametrized date ranges in DAGs [RECOMMENDED], b) Separate backfill scripts, c) Full rebuild."
- **Schema Evolution:** "What happens when the upstream API adds or removes a column? a) Alert and halt pipeline [RECOMMENDED], b) Auto-evolve target schema, c) Ignore unknown columns."

## 4. Mobile Application
- **Offline Strategy:** "How does the app behave without an internet connection? a) Read-only cache [RECOMMENDED], b) Full offline-first with local mutations and sync, c) Force network connection."
- **State Management:** "How is local state synced with the remote database? a) REST polling [RECOMMENDED], b) GraphQL/Apollo cache, c) Real-time WebSockets/Supabase."
- **Push Notifications:** "What triggers push notifications? a) Server-side cron jobs [RECOMMENDED], b) Direct Firebase/APNs integration, c) User-to-user events."

## 5. AI / LLM Product
- **Model Routing:** "How are you handling token limits and model fallbacks? a) Single provider (e.g., OpenAI) [RECOMMENDED], b) Router like LiteLLM for fallback/cost optimization."
- **Context Management:** "How is conversation history or RAG context injected? a) Sliding window of last N messages [RECOMMENDED], b) Vector DB retrieval, c) Summarization compression."
- **Guardrails:** "How do you prevent the AI from generating harmful or out-of-scope content? a) System prompt rules only [RECOMMENDED], b) Secondary evaluation model, c) Keyword filtering."

## 6. Internal Tool / Admin Panel
- **Data Sources:** "Is this tool writing directly to production databases? a) Yes, via an ORM [RECOMMENDED], b) No, via internal APIs only, c) Read-only access."
- **Audit Logging:** "Do you need an immutable audit trail of who changed what? a) Basic updated_by timestamps [RECOMMENDED], b) Full event sourcing/audit tables, c) Not required."
- **Deployment:** "Where will this tool be hosted to ensure internal security? a) VPN/VPC only, b) Public web with SSO [RECOMMENDED], c) Localhost only."
