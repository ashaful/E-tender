# Phase 1 Missing Requirements - VendorBid

Based on the current `/opt/odoo18/custom_addons/VendorBid` code compared with the attached Phase 1 BRD.

## BR-01 Vendor Registration & Approval
- Draft save and correction-required workflow is missing. Current registration starts as submitted and supports approved/finalized/rejected/blacklisted only.
- Mandatory legal/tax/financial/experience data is incomplete: operating address, mobile, official email separation, vendor category plus multiple product/service categories, trade license issue date, BIN/VAT applicability, income tax return assessment/receipt, annual turnover for latest 3 years, audited statement/auditor details, detailed experience entries, declaration are missing or partial.
- Required document set is incomplete: TIN certificate, income tax return, BIN/VAT conditional certificate, annual turnover evidence for 3 years, audited financial statements up to 3 years, relevant experience evidence, company profile, authorization letter are missing or not separately modeled.
- Mandatory/optional document configuration by vendor category is missing.
- Final submission validation for all mandatory fields/documents is incomplete; many document fields are optional.
- Expired Trade License or validity-controlled documents do not block vendor eligibility after approval.
- Return for Correction with reason is missing.
- Approved and Active eligibility control is incomplete; eligibility is mostly based on `supplier_rank > 0`.

## BR-02 Requester Request
- No proper internal request model/workflow exists for business requests. Current `supplies.requester` is requester user registration, not product/service/work request.
- Missing request number/date, requester department, request category, title, justification, detailed specification, product/service lines with UoM and delivery date, budget/currency/location, recommended vendor category and attachments.
- Missing workflow Draft -> Submitted -> Approved / Rejected / Correction Required.
- Missing rule that only approved requests can create an RFP.
- Missing retained source request reference on RFP.
- Missing control to prevent requester self-approval.

## BR-03 RFP Creation & Approval
- RFP fields are incomplete: linked request number, title, public/private visibility, publish date/time deadline, expected delivery/completion date, detailed scope, technical specification, location, buyer contact, eligibility requirements, payment terms, bid validity, pricing instructions, mandatory bid fields/documents, terms/declaration/downloadable attachments are missing or partial.
- RFP workflow does not match required flow: Draft -> Submitted for Approval -> Approved -> Published -> Closed -> Awarded / Cancelled. Current flow uses draft/submitted/approved/closed/recommendation/accepted/rejected.
- No separate Published/Open state.
- Publication validation is incomplete: no mandatory deadline, visibility, scope, documents, or full required-field checks.
- RFP cancellation with mandatory cancellation reason is missing.

## BR-04 Public / Private RFP Visibility
- Public/private visibility field is missing.
- Private RFP selected-vendor list is missing.
- Private RFP authorization by selected approved vendors is missing.
- Copied-link protection for private RFPs is missing.
- Public RFP visitor summary page is missing; portal RFP list requires login.
- Public visitor register/login continuation flow is missing.
- Approved/Active/category eligibility for final public bidding is incomplete.

## BR-05 Publish & Email Invitation
- No explicit publish action/event; supplier emails are sent on RFP approval.
- Private RFP invitation to selected vendors is missing.
- Public RFP email to all approved and active category-matched vendors is only partial; it does not check active/private/public rules.
- Duplicate invitation prevention per publication event is missing.
- Mandatory email content is incomplete: buyer contact, scope, quantity/location, deadline with timezone, eligibility summary, mandatory bid documents, commercial instructions, clear bid button/clickable RFP number are not fully implemented.
- Login redirect back to same RFP is missing.
- Public visitor link behavior is missing.

## BR-06 Deadline & Auto-close
- Submission deadline with exact time and timezone is missing; current `required_date` is date-only.
- Automatic close at deadline is missing. Existing cron only deletes rejected requesters.
- Portal does not block bid submission after deadline.
- Late bid prevention is missing.
- Deadline extension with mandatory reason is missing.
- Email notification for deadline extension is missing.
- Old/revised deadline history is missing.

## BR-07 Vendor Bid Submission
- No dedicated bid model exists; vendor bid is stored as `purchase.order` RFQ.
- Mandatory bid data is incomplete: vendor bid reference, quotation date, bid validity, discount, VAT/tax at bid summary level, other charges, currency control, total bid amount, lead time, payment terms, warranty/service support, experience summary, compliance response, terms acceptance are missing or partial.
- Mandatory bid documents are missing: signed financial quotation, technical proposal/compliance document, experience evidence, and RFP-defined mandatory documents.
- Draft bid save/edit until final submission/deadline is missing.
- Final submission and bid locking are missing.
- Mandatory field/price/document validation before final submission is incomplete.
- Timestamped submission acknowledgement is missing.
- Procurement-only visibility after RFP close is missing; internal users can see RFQs before close.

## BR-08 Bid Review & Decision
- Review is based on purchase RFQ recommendation/acceptance, not the required bid decision workflow.
- Clarification Required decision is missing.
- Accepted/Rejected decision reasons are missing or incomplete for bids.
- Acceptance reason and authorized approver control are missing.
- RFP status should become Awarded; current status becomes `accepted`.
- Decision lock from ordinary vendor users is not explicitly implemented.
- Acceptance email to selected vendor and non-selection emails to others are missing.
- Minimum review information is incomplete: evaluated total, document completion status, procurement review note, decision reason are missing or partial.

## BR-09 Purchase Handover
- Purchase handover is partially implemented by confirming the accepted RFQ, but it does not create a separate standard draft RFQ/PO from an accepted bid as required.
- Purchase document does not retain all required links: original Request and accepted Bid links are missing; only RFP link exists.
- Accepted bid evidence preservation cannot be satisfied because bid evidence/documents are not modeled.
- Payment terms, delivery terms, full taxes and commercial details are incomplete.

## BR-10 Roles, Access & Record Protection
- Required role split is incomplete: requester, request approver, procurement user, RFP approver, vendor are not fully represented as separate permissions.
- Request access/approval rules are missing because proper request records are missing.
- Procurement authority to create/publish/close/evaluate RFPs is not fully separated.
- Portal vendor access uses sudo in portal routes and depends on custom domains; private RFP and copied-link protection is not fully implemented.
- Other-vendor bid/RFP confidentiality is incomplete, especially before close and for private RFPs.
- Activity history is incomplete for critical events: publication, deadline changes, bid final submission, bid decisions, acceptance/rejection reasons, cancellation.

## Definition of Done Gaps
- BR-01 through BR-10 are not fully complete.
- Mandatory field and attachment validation is not complete in both backend and portal.
- Public/private RFP access rules are missing.
- Category-based invitation with correct login/registration return is incomplete.
- Auto-close and late-submission blocking are missing.
- Complete bid submission with timestamped acknowledgement is missing.
- Linked purchase document from accepted bid is only partial.
- Separate-user access testing for requester, approver, procurement and vendor cannot fully pass with the current role model.
