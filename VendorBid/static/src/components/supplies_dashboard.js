/** @odoo-module */
import { registry } from "@web/core/registry"
const { Component, onWillStart, useState, useEffect } = owl;
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { StatBar } from "./statbar/statbar";
import { Graph } from "./graph/graph";
import { CompanyCard } from "./company_card/company_card";
import { formatAmount, getDateInterval, groupProducts, getCurrency } from './utils'


export class SuppliesDashboard extends Component {
    setup() {
        this.timeperiods = [
            { tag: 'this_week', label: 'This Week' },
            { tag: 'last_week', label: 'Last Week' },
            { tag: 'last_month', label: 'Last Month' },
            { tag: 'last_year', label: 'Last Year' },
        ];
        this.state = useState({
            suppliers: [],
            selectedSupplierId: "0",
            currency: '',
            selectedPeriod: "0",
            productLineIds: [],
            productLines: [],
            rfpPurchaseChartData: null,
            rfqStatusChartData: null,
            another: 'test',
            rfp: {
                'accepted': 0,
                'submitted': 0,
                'total_amount': 0,
            },
            overview: this.getEmptyOverview(),
        })
        this.orm = useService('orm');
        this.action = useService('action');

        onWillStart(async () => {
            await this.getSuppliers();
            await this.getOverview();
        });

        useEffect(() => {
            if (this.state.selectedSupplierId !== "0") {
                this.getRequestForPurchases();
            } else {
                this.state.rfp = { accepted: 0, submitted: 0, total_amount: 0 };
                this.state.rfpPurchaseChartData = null;
                this.state.rfqStatusChartData = null;
                this.state.productLines = [];
                this.state.productLineIds = [];
                this.getOverview();
            }
        }, () => [this.state.selectedSupplierId, this.state.selectedPeriod]);

        useEffect(() => {
            if (this.state.productLineIds.length) {
                this.getProductLines();
            } else {
                this.state.productLines = [];
            }
        }, () => [this.state.productLineIds]);

    }

    async getSuppliers() {
        const suppliers = await this.orm.searchRead(
            'res.partner',
            [['supplier_rank', '>', 0]],
            ['name', 'image_1920', 'street', 'active', 'vendor_document_complete']
        );
        this.state.suppliers = suppliers;        
    }

    getEmptyOverview() {
        return {
            loading: true,
            stats: {
                totalRfps: 0,
                publishedRfps: 0,
                awaitingDecision: 0,
                rfpReviewQueue: 0,
                awardedRfps: 0,
                awardedValue: '0.00',
                activeVendors: 0,
                documentReadyVendors: 0,
                decisionCoverage: '0%',
                averageQuotes: '0.0',
            },
            pendingQuotes: [],
            highValueQuotes: [],
            upcomingDeadlines: [],
            rfpPipeline: [],
            rfpStatusChartData: null,
            bidDecisionChartData: null,
        };
    }

    getPeriodDomain(fieldName) {
        if (this.state.selectedPeriod === "0") {
            return [];
        }
        const { start, end } = getDateInterval(this.state.selectedPeriod);
        return [[fieldName, '>=', start], [fieldName, '<=', end]];
    }

    get selectedPeriodLabel() {
        return this.timeperiods.find((period) => period.tag === this.state.selectedPeriod)?.label || 'All Time';
    }

    async getOverview() {
        this.state.overview.loading = true;
        const rfpDomain = this.getPeriodDomain('create_date');
        const rfqDomain = [['rfp_id', '!=', false], ...this.getPeriodDomain('create_date')];

        const [rfps, quotations] = await Promise.all([
            this.orm.call('supplies.rfp', 'get_rfp_sudo', [rfpDomain, [
                'rfp_number', 'rfp_title', 'state', 'submission_deadline', 'required_date',
                'num_rfq', 'total_amount', 'currency_id', 'visibility',
            ]]),
            this.orm.call('purchase.order', 'get_purchase_order_sudo', [rfqDomain, [
                'name', 'partner_id', 'rfp_id', 'state', 'bid_decision', 'amount_total',
                'bid_submitted_at', 'date_planned', 'score', 'recommended',
            ]]),
        ]);

        const activeQuotes = quotations.filter((quote) => quote.state !== 'cancel');
        const awaitingDecision = activeQuotes.filter((quote) => quote.bid_decision === 'pending');
        const awardedQuotes = quotations.filter((quote) => quote.bid_decision === 'accepted' || quote.state === 'purchase');
        const publishedRfps = rfps.filter((rfp) => rfp.state === 'published');
        const activeVendors = this.state.suppliers.filter((supplier) => supplier.active).length;
        const documentReadyVendors = this.state.suppliers.filter(
            (supplier) => supplier.active && supplier.vendor_document_complete
        ).length;
        const reviewRfps = rfps.filter((rfp) => ['closed', 'recommendation'].includes(rfp.state));
        const awardedRfps = rfps.filter((rfp) => rfp.state === 'awarded');
        const decidedQuotes = activeQuotes.filter((quote) => quote.bid_decision !== 'pending');
        const quoteRows = (quotes) => quotes.map((quote) => ({
            ...quote,
            amount_display: formatAmount(quote.amount_total),
            vendor_name: quote.partner_id ? quote.partner_id[1] : '-',
            rfp_number: quote.rfp_id ? quote.rfp_id[1] : '-',
            submitted_display: quote.bid_submitted_at || '-',
            decision_label: this.getDecisionLabel(quote.bid_decision),
        }));

        this.state.overview = {
            loading: false,
            stats: {
                totalRfps: rfps.length,
                publishedRfps: publishedRfps.length,
                awaitingDecision: awaitingDecision.length,
                rfpReviewQueue: reviewRfps.length,
                awardedRfps: awardedRfps.length,
                awardedValue: formatAmount(awardedQuotes.reduce((total, quote) => total + (quote.amount_total || 0), 0)),
                activeVendors,
                documentReadyVendors,
                decisionCoverage: activeQuotes.length ? `${Math.round((decidedQuotes.length / activeQuotes.length) * 100)}%` : '0%',
                averageQuotes: rfps.length ? (quotations.length / rfps.length).toFixed(1) : '0.0',
            },
            pendingQuotes: awaitingDecision
                .sort((left, right) => new Date(right.bid_submitted_at || 0) - new Date(left.bid_submitted_at || 0))
                .slice(0, 6)
                .map((quote) => quoteRows([quote])[0]),
            highValueQuotes: activeQuotes
                .sort((left, right) => (right.amount_total || 0) - (left.amount_total || 0))
                .slice(0, 5)
                .map((quote) => quoteRows([quote])[0]),
            upcomingDeadlines: publishedRfps
                .filter((rfp) => rfp.submission_deadline)
                .sort((left, right) => new Date(left.submission_deadline) - new Date(right.submission_deadline))
                .slice(0, 5),
            rfpPipeline: this.getRfpPipeline(rfps),
            rfpStatusChartData: this.getRfpStatusChartData(rfps),
            bidDecisionChartData: this.getBidDecisionChartData(quotations),
        };
    }

    getDecisionLabel(decision) {
        return {
            pending: 'Pending',
            accepted: 'Accepted',
            rejected: 'Rejected',
            clarification: 'Clarification',
        }[decision] || 'Pending';
    }

    getRfpPipeline(rfps) {
        const stages = [
            ['submitted', 'Submitted', 'pipeline-submitted'],
            ['approved', 'Approved', 'pipeline-approved'],
            ['published', 'Published', 'pipeline-published'],
            ['closed', 'Evaluation', 'pipeline-evaluation'],
            ['recommendation', 'Recommendation', 'pipeline-recommendation'],
            ['awarded', 'Awarded', 'pipeline-awarded'],
        ];
        return stages.map(([state, label, style]) => ({
            label,
            style,
            count: rfps.filter((rfp) => rfp.state === state).length,
        }));
    }

    getRfpStatusChartData(rfps) {
        const stages = [
            ['draft', 'Draft'],
            ['submitted', 'Submitted'],
            ['approved', 'Approved'],
            ['published', 'Published'],
            ['closed', 'Closed'],
            ['recommendation', 'Recommendation'],
            ['awarded', 'Awarded'],
            ['cancelled', 'Cancelled'],
        ];
        return {
            labels: stages.map(([, label]) => label),
            datasets: [{
                label: 'RFPs',
                data: stages.map(([state]) => rfps.filter((rfp) => rfp.state === state).length),
                backgroundColor: ['#94a3b8', '#60a5fa', '#a78bfa', '#14b8a6', '#f59e0b', '#6366f1', '#22c55e', '#f87171'],
                borderRadius: 5,
            }],
        };
    }

    getBidDecisionChartData(quotations) {
        const decisions = [
            ['pending', 'Pending'],
            ['accepted', 'Accepted'],
            ['rejected', 'Rejected'],
            ['clarification', 'Clarification'],
        ];
        return {
            labels: decisions.map(([, label]) => label),
            datasets: [{
                label: 'Quotations',
                data: decisions.map(([decision]) => quotations.filter((quote) => quote.bid_decision === decision).length),
                backgroundColor: ['#f59e0b', '#22c55e', '#ef4444', '#3b82f6'],
            }],
        };
    }

    openQuotation(event) {
        const quotationId = Number(event.currentTarget.dataset.quotationId);
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'purchase.order',
            res_id: quotationId,
            views: [[false, 'form']],
            target: 'current',
        });
    }

    openRfp(event) {
        const rfpId = Number(event.currentTarget.dataset.rfpId);
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'supplies.rfp',
            res_id: rfpId,
            views: [[false, 'form']],
            target: 'current',
        });
    }

    setRfpPurchaseData(purchase_orders) {
        if (purchase_orders.length == 0) {
            this.state.rfpPurchaseChartData = null;
            return;
        }
        const data = {
            labels: purchase_orders.map(po => po.name),
            datasets: [
                {
                    label: 'Total Amount',
                    data: purchase_orders.map(po => po.amount_untaxed)
                }
            ]
        }
        this.state.rfpPurchaseChartData = data;
    }

    setRFQStatusData(rfqs) {        
        if (rfqs.length == 0) {
            this.state.rfqStatusChartData = null;
            return;
        }
        const purchase = rfqs.filter(r => r.state === 'purchase').length;
        const draft = rfqs.filter(r => r.state === 'draft').length;
        const cancel = rfqs.filter(r => r.state === 'cancel').length;
        const data = {
            labels: ['Accepted', 'Draft', 'Cancelled'],
            datasets: [
                {
                    label: 'Count',
                    data: [purchase, draft, cancel],
                    backgroundColor: [
                        '#06d6a0',
                        '#468faf',
                        'rgb(255, 99, 132)'
                    ],
                }
            ]
        }
        this.state.rfqStatusChartData = data;
    }

    async getRequestForPurchases() {
        const rfq_domain = [['rfp_id', '!=', false]];
        const purchase_order_domain = [['state', '=', 'purchase']];
        if (this.state.selectedSupplierId !== "0") {
            const supplerIdInt = parseInt(this.state.selectedSupplierId);
            const partner_subdomain = ['partner_id', '=', supplerIdInt];
            rfq_domain.push(partner_subdomain);
            purchase_order_domain.push(partner_subdomain);
        } else {
            return;
        }
        if (this.state.selectedPeriod !== "0") {
            const { start: startDate, end: endDate } = getDateInterval(this.state.selectedPeriod);
            rfq_domain.push(...[['create_date', '>=', startDate], ['create_date', '<=', endDate]]);
            purchase_order_domain.push(['date_approve', '>=', startDate], ['date_approve', '<=', endDate]);
        }

        const purchase_orders = await this.orm.call(
            'purchase.order',
            'get_purchase_order_sudo', 
            [purchase_order_domain, ['name', 'amount_untaxed', 'order_line']]
        );
        const rfqs = await this.orm.call(
            'purchase.order',
            'get_purchase_order_sudo', 
            [rfq_domain, ['state']]
        );
        const submitted = rfqs.length;
        const accepted = purchase_orders.length;
        let total_amount = purchase_orders.reduce((acc, r) => acc + r.amount_untaxed, 0);
        if (!isNaN(total_amount) && total_amount > 0) {
            total_amount = formatAmount(total_amount);
        }
        const productLineIds = purchase_orders.map(r => r.order_line).flat();
        this.state.productLineIds = productLineIds;
        this.state.rfp = { accepted, submitted, total_amount };
        this.setRfpPurchaseData(purchase_orders);
        this.setRFQStatusData(rfqs);
    }

    async getProductLines() {
        const productLines = await this.orm.searchRead(
            'purchase.order.line',
            [['id', 'in', this.state.productLineIds]],
            ['product_id', 'currency_id', 'product_name', 'product_qty', 'price_unit', 'price_subtotal', 'product_image', 'rfp_id']
        );
        this.state.productLines = groupProducts(productLines);
        this.state.currency = getCurrency(productLines);
    }
}

SuppliesDashboard.template = 'supplies.dashboard';
SuppliesDashboard.components = { Layout, Graph, StatBar, CompanyCard };

registry.category("actions").add("supplies.dashboard", SuppliesDashboard);
