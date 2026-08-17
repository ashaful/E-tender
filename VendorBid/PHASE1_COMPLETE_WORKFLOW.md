# VendorBid Phase 1 Workflow

This document describes the implemented Phase 1 operating workflow after the important requirement fixes and the latest hardening changes.

## New in This Change

- Added configurable vendor mandatory document matrix by vendor/product category.
- Added vendor document completeness validation before registration finalization.
- Added separate bid document upload fields:
  - Signed Financial Quotation
  - Technical Proposal / Compliance
  - Relevant Experience Evidence
  - RFP-Specific Mandatory Documents
- Added public anonymous RFP summary page before login.
- Added invitation email content with RFP title, category, scope, deadline, buyer contact, location, mandatory documents and direct login-return link.
- Added formal bid decision email templates:
  - Acceptance
  - Non-selection
  - Rejection
  - Clarification required
- Added bid decision email sending from accept/reject/clarification actions.
- Added a required-reason Bid Decision dialog before accepting, rejecting or requesting clarification on a bid.
- Added an organization-wide procurement overview as the default Dashboard view; vendor selection continues to open the existing individual vendor analysis.
- Expanded the approver overview with RFP review workload, decision coverage, vendor document readiness, RFP pipeline, high-value quotations and submission deadlines.
- Tightened backend record rules:
  - Requesters see their own procurement requests.
  - Approvers see submitted/decision procurement requests.
  - Portal users can read only their own submitted RFQs.
- Added upgrade-safe guard so vendor finalization does not crash if the new document matrix table has not yet been created during deployment.

## 1. Vendor Registration

1. Vendor opens the website registration form.
2. Vendor submits company, contact, bank, tax/license, category and supporting document information.
3. Reviewer reviews the registration record.
4. Reviewer can approve, reject, or blacklist the registration.
5. Approved registration can be finalized into a standard Odoo vendor/contact and portal user.
6. On finalization, the system checks the vendor category document matrix.
7. If required category documents are missing, finalization is blocked with the missing document names.
8. Only finalized vendors with `supplier_rank > 0`, active status and complete required category documents are treated as eligible for invitations.

## 1A. Vendor Document Matrix

1. Procurement configures document requirements from `Procurement > Vendor Document Matrix`.
2. Each matrix line defines:
   - Vendor/product category
   - Document field
   - Mandatory or optional status
   - Active/inactive status
3. The matrix can be different per category.
4. The matrix is used during vendor finalization and RFP vendor invitation filtering.
5. If no matrix is configured for a category, the system does not block that category by document matrix.

## 2. Internal Procurement Request

1. Requester creates a Procurement Request from `Procurement > Procurement Requests`.
2. Requester fills:
   - Request category: Product, Service or Work
   - Title
   - Business justification
   - Detailed specification
   - Vendor/product category
   - Budget, currency and delivery location
   - Product/service/work lines with quantity, UoM, required date and expected price
   - Supporting attachment when needed
3. Requester submits the request.
4. Request Approver reviews the request.
5. Approver can:
   - Approve
   - Reject, with reason
   - Return for correction, with reason
6. Requester self-approval is blocked unless the user is authorized as approver.
7. Only an approved request can create an RFP.

## 3. RFP Creation

1. Procurement opens the approved Procurement Request and clicks `Create RFP`.
2. The system creates an RFP linked to the source request.
3. Procurement completes the RFP:
   - RFP title
   - Public or Private visibility
   - Product/vendor category
   - Exact bid submission deadline
   - Scope/specification
   - Delivery/work location
   - Buyer contact
   - Eligibility requirements
   - Payment terms
   - Bid validity
   - Pricing instructions
   - Mandatory bid documents
   - Terms and conditions
   - RFP attachment
   - Product/pricing lines
4. For Private RFPs, Procurement selects the authorized vendors.
5. Procurement submits the RFP for approval.
6. RFP Approver approves or rejects the RFP.

## 4. RFP Publishing

1. Procurement publishes only an approved RFP.
2. Publication is blocked if required publish data is missing:
   - Submission deadline
   - Product category
   - Product/pricing lines
   - RFP title
   - Scope/specification
   - Selected vendors for Private RFP
3. On publish:
   - RFP status becomes `Published`
   - Publish date is recorded
   - RFP becomes visible in the vendor portal
   - Invitation emails are sent to eligible vendors
4. Public RFP invitation goes to active approved vendors matching the category and document matrix.
5. Private RFP invitation goes only to selected active approved vendors whose required category documents are complete.
6. Duplicate invitation emails are avoided within the same publication run.
7. Invitation email contains the RFP number/title, category, scope, deadline, buyer contact, location, mandatory documents and direct `View RFP & Submit Bid` login-return URL.

## 5. Vendor Portal Visibility

1. Vendor logs in to the portal.
2. Vendor sees only Published RFPs.
3. Category filtering is applied.
4. Public RFPs are visible to category-matched approved vendors.
5. Private RFPs are visible only to selected authorized vendors.
6. Unauthorized private RFP access through a copied link is blocked.
7. Anonymous visitors can open the public RFP summary page at `/supplies/rfp/<RFP Number>`.
8. The public page shows summary, deadline, eligibility, scope and requested lines, then offers Login or Register.

## 6. Vendor Bid Submission

1. Vendor opens an eligible Published RFP.
2. Vendor submits the bid through the existing portal RFQ form.
3. The system checks before accepting the bid:
   - Vendor is an approved supplier
   - RFP is Published
   - Deadline has not passed
   - Private RFP vendor is selected/authorized
   - Required price line data passes schema validation
   - Signed financial quotation is uploaded
   - Technical proposal/compliance document is uploaded
   - Relevant experience evidence is uploaded
   - RFP-specific documents are uploaded when the RFP marks them mandatory
4. Incomplete bid document submissions are rejected and the temporary RFQ is removed.
5. The submitted bid is stored as an Odoo `purchase.order` RFQ linked to the RFP.
6. Bid submission timestamp is recorded.
7. Vendor can view only its own submitted RFQs from the portal.

## 7. Deadline and Auto-close

1. Every published RFP has an exact `submission_deadline`.
2. A scheduled job runs every 15 minutes.
3. Published RFPs whose deadline has passed are automatically moved to `Closed`.
4. Portal submission is immediately blocked when the deadline has passed.
5. Procurement can update the deadline before evaluation.
6. Old deadline is retained when the deadline changes.
7. Deadline extension reason can be recorded in the RFP chatter.

## 8. Bid Review and Decision

1. Procurement reviews RFQs after the RFP is Closed.
2. Procurement can mark a bid:
   - Recommended
   - Rejected, with decision reason
   - Clarification Required, with decision reason
3. RFP can move to Recommendation after at least one RFQ is recommended.
4. Approver selects **Accept** on the selected RFQ and enters the acceptance reason in the Bid Decision dialog.
5. The Bid Decision dialog requires a reason before an accept, reject or clarification decision can be submitted.
6. Acceptance requires the decision reason and required bid documents.
7. Accepted RFQ is confirmed into the standard Odoo purchase process.
8. Selected vendor receives a formal acceptance email.
9. Competing RFQs are cancelled and marked rejected with a standard non-selection reason.
10. Non-selected submitted vendors receive a formal non-selection email.
11. Manual rejection sends a formal rejection email.
12. Clarification Required sends a formal clarification email.
13. RFP status becomes `Awarded`.

## 9. Purchase Handover

1. Accepted vendor bid continues into Odoo Purchase using the existing RFQ/PO record.
2. Purchase document retains the RFP link.
3. Selected vendor, product lines, quantities, prices and taxes from the bid are retained.
4. Existing submitted bid/RFQ evidence is not overwritten during acceptance.
5. Bid documents remain attached to the accepted RFQ/PO.

## 10. Roles and Access

1. Requester users can create and submit Procurement Requests.
2. Request Approvers can approve, reject or return requests.
3. Procurement/Reviewer users can create and manage RFPs.
4. RFP Approvers can approve/reject submitted RFPs and accept recommended bids.
5. Portal vendors can access only their own profile, eligible RFPs and own RFQs.
6. Private RFP access is restricted by selected vendor list.
7. Requesters can access only their own procurement requests.
8. Request approvers can access submitted/approved/rejected/correction requests for decision work.
9. Important status changes are tracked in chatter/activity history.

## Current Architecture Note

- Vendor bids continue to use Odoo `purchase.order` RFQs as the bid record. This preserves native purchase handover and avoids duplicating purchase data.
- A future dedicated bid model can still be introduced if the organization later needs sealed-bid opening, complex bid versioning or committee evaluation beyond Phase 1.
