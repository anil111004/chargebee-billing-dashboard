import { apiGet, apiPost } from './services/api';
import { useEffect, useMemo, useState } from 'react';

const navItems = ['Dashboard', 'Customers', 'Subscriptions', 'Invoices'];

function App() {
  const [activePage, setActivePage] = useState('Dashboard');
  const [dashboard, setDashboard] = useState({ metrics: {}, recent_subscriptions: [], recent_invoices: [] });
  const [customers, setCustomers] = useState({ items: [], page: 1, limit: 10, total: 0, source: 'demo' });
  const [subscriptions, setSubscriptions] = useState({ items: [], page: 1, limit: 10, total: 0, source: 'demo' });
  const [invoices, setInvoices] = useState({ items: [], page: 1, limit: 10, total: 0, source: 'demo' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [customerSearch, setCustomerSearch] = useState('');
  const [subscriptionSearch, setSubscriptionSearch] = useState('');
  const [subscriptionStatus, setSubscriptionStatus] = useState('all');
  const [invoiceSearch, setInvoiceSearch] = useState('');
  const [form, setForm] = useState({ customer_id: '', plan_id: '', item_price_id: '', trial_end: '' });

  const loadDashboard = async () => {
    try {
      const data = await apiGet('/api/dashboard');
      setDashboard(data);
    } catch (err) {
      setError(err.message || 'Dashboard load failed.');
    }
  };

  const loadCustomers = async (page = 1, query = customerSearch) => {
    try {
      const data = await apiGet('/api/customers', { page, limit: 10, search: query });
      setCustomers({ ...data, page });
    } catch (err) {
      setError(err.message || 'Customer data could not be loaded.');
    }
  };

  const loadSubscriptions = async (page = 1, status = subscriptionStatus, query = subscriptionSearch) => {
    try {
      const data = await apiGet('/api/subscriptions', { page, limit: 10, status, search: query });
      setSubscriptions({ ...data, page });
    } catch (err) {
      setError(err.message || 'Subscription data could not be loaded.');
    }
  };

  const loadInvoices = async (page = 1, query = invoiceSearch) => {
    try {
      const data = await apiGet('/api/invoices', { page, limit: 10, search: query });
      setInvoices({ ...data, page });
    } catch (err) {
      setError(err.message || 'Invoice data could not be loaded.');
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  useEffect(() => {
    if (activePage === 'Customers') {
      loadCustomers(1, customerSearch);
    }
  }, [activePage, customerSearch]);

  useEffect(() => {
    if (activePage === 'Subscriptions') {
      loadSubscriptions(1, subscriptionStatus, subscriptionSearch);
    }
  }, [activePage, subscriptionStatus, subscriptionSearch]);

  useEffect(() => {
    if (activePage === 'Invoices') {
      loadInvoices(1, invoiceSearch);
    }
  }, [activePage, invoiceSearch]);

  const handleCreateSubscription = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    if (!form.customer_id || (!form.plan_id && !form.item_price_id)) {
      setError('Customer ID and either Plan ID or Item Price ID are required.');
      setLoading(false);
      return;
    }

    try {
      const payload = {
        customer_id: form.customer_id,
        plan_id: form.plan_id || '',
        item_price_id: form.item_price_id || '',
        trial_end: form.trial_end ? Number(form.trial_end) : '',
      };
      const created = await apiPost('/api/subscriptions', payload);
      setForm({ customer_id: '', plan_id: '', item_price_id: '', trial_end: '' });
      await loadSubscriptions(1, subscriptionStatus, subscriptionSearch);
      setActivePage('Subscriptions');
      setError('');
      if (created?.subscription) {
        alert('Subscription created successfully.');
      }
    } catch (err) {
      setError(err.message || 'Subscription could not be created.');
    } finally {
      setLoading(false);
    }
  };

  const metricCards = [
    { label: 'Total customers', value: dashboard.metrics.total_customers || 0 },
    { label: 'Active subscriptions', value: dashboard.metrics.active_subscriptions || 0 },
    { label: 'Trials in progress', value: dashboard.metrics.trials_in_progress || 0 },
    { label: 'Invoice total', value: formatCurrency(dashboard.metrics.invoice_total || 0) },
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">C</div>
          <div>
            <h2>Chargebee</h2>
            <small>Billing Dashboard</small>
          </div>
        </div>

        <nav className="nav">
          {navItems.map((item) => (
            <button
              key={item}
              type="button"
              className={item === activePage ? 'nav-item active' : 'nav-item'}
              onClick={() => setActivePage(item)}
            >
              {item}
            </button>
          ))}
        </nav>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Overview</p>
            <h1>{activePage}</h1>
          </div>
          <div className="pill">{dashboard.source === 'demo' ? 'Demo mode active' : 'Live Chargebee data'}</div>
        </header>

        {error ? <div className="alert">{error}</div> : null}

        {activePage === 'Dashboard' && (
          <>
            <section className="stats-grid">
              {metricCards.map((card) => (
                <div key={card.label} className="stat-card">
                  <span>{card.label}</span>
                  <strong>{card.value}</strong>
                </div>
              ))}
            </section>

            <section className="content-grid">
              <div className="panel">
                <div className="panel-header">
                  <h3>Recent subscriptions</h3>
                </div>
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Customer</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboard.recent_subscriptions.length ? (
                      dashboard.recent_subscriptions.map((sub) => (
                        <tr key={sub.id}>
                          <td>{sub.id}</td>
                          <td>{sub.customer_id}</td>
                          <td><span className={`badge status-${sub.status || 'unknown'}`}>{sub.status || 'N/A'}</span></td>
                        </tr>
                      ))
                    ) : (
                      <tr><td colSpan="3">No recent subscriptions available.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h3>Recent invoices</h3>
                </div>
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Customer</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboard.recent_invoices.length ? (
                      dashboard.recent_invoices.map((invoice) => (
                        <tr key={invoice.id}>
                          <td>{invoice.id}</td>
                          <td>{invoice.customer_id}</td>
                          <td><span className={`badge status-${invoice.status || 'unknown'}`}>{invoice.status || 'N/A'}</span></td>
                        </tr>
                      ))
                    ) : (
                      <tr><td colSpan="3">No recent invoices available.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}

        {activePage === 'Customers' && (
          <section className="panel">
            <div className="panel-header">
              <h3>Customers</h3>
              <input
                type="search"
                value={customerSearch}
                onChange={(e) => setCustomerSearch(e.target.value)}
                placeholder="Search customers"
              />
            </div>
            <table>
              <thead>
                <tr>
                  <th>Customer ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {customers.items.length ? (
                  customers.items.map((customer) => (
                    <tr key={customer.id}>
                      <td>{customer.id}</td>
                      <td>{customer.name || 'Unknown customer'}</td>
                      <td>{customer.email}</td>
                      <td>{formatDate(customer.created_at)}</td>
                    </tr>
                  ))
                ) : (
                  <tr><td colSpan="4">No customers found.</td></tr>
                )}
              </tbody>
            </table>
            <div className="pagination">
              <button onClick={() => loadCustomers(Math.max(1, customers.page - 1), customerSearch)} disabled={customers.page <= 1}>Previous</button>
              <span>Page {customers.page}</span>
              <button onClick={() => loadCustomers(customers.page + 1, customerSearch)}>Next</button>
            </div>
          </section>
        )}

        {activePage === 'Subscriptions' && (
          <>
            <section className="panel form-panel">
              <div className="panel-header">
                <h3>Create subscription</h3>
              </div>
              <form onSubmit={handleCreateSubscription} className="subscription-form">
                <input
                  placeholder="Customer ID"
                  value={form.customer_id}
                  onChange={(e) => setForm({ ...form, customer_id: e.target.value })}
                />
                <input
                  placeholder="Plan ID"
                  value={form.plan_id}
                  onChange={(e) => setForm({ ...form, plan_id: e.target.value })}
                />
                <input
                  placeholder="Item price ID"
                  value={form.item_price_id}
                  onChange={(e) => setForm({ ...form, item_price_id: e.target.value })}
                />
                <input
                  type="number"
                  placeholder="Trial end timestamp"
                  value={form.trial_end}
                  onChange={(e) => setForm({ ...form, trial_end: e.target.value })}
                />
                <button type="submit" disabled={loading}>{loading ? 'Creating...' : 'Create subscription'}</button>
              </form>
            </section>

            <section className="panel">
              <div className="panel-header">
                <h3>Subscriptions</h3>
                <div className="filters">
                  <select value={subscriptionStatus} onChange={(e) => setSubscriptionStatus(e.target.value)}>
                    <option value="all">All statuses</option>
                    <option value="active">Active</option>
                    <option value="trialing">Trialing</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                  <input
                    type="search"
                    value={subscriptionSearch}
                    onChange={(e) => setSubscriptionSearch(e.target.value)}
                    placeholder="Search subscriptions"
                  />
                </div>
              </div>
              <table>
                <thead>
                  <tr>
                    <th>Subscription ID</th>
                    <th>Customer</th>
                    <th>Plan</th>
                    <th>Status</th>
                    <th>Trial end</th>
                  </tr>
                </thead>
                <tbody>
                  {subscriptions.items.length ? (
                    subscriptions.items.map((sub) => (
                      <tr key={sub.id}>
                        <td>{sub.id}</td>
                        <td>{sub.customer_id}</td>
                        <td>{sub.plan_id || sub.item_price_id || 'N/A'}</td>
                        <td><span className={`badge status-${sub.status || 'unknown'}`}>{sub.status || 'N/A'}</span></td>
                        <td>{formatDate(sub.trial_end)}</td>
                      </tr>
                    ))
                  ) : (
                    <tr><td colSpan="5">No subscriptions found.</td></tr>
                  )}
                </tbody>
              </table>
              <div className="pagination">
                <button onClick={() => loadSubscriptions(Math.max(1, subscriptions.page - 1), subscriptionStatus, subscriptionSearch)} disabled={subscriptions.page <= 1}>Previous</button>
                <span>Page {subscriptions.page}</span>
                <button onClick={() => loadSubscriptions(subscriptions.page + 1, subscriptionStatus, subscriptionSearch)}>Next</button>
              </div>
            </section>
          </>
        )}

        {activePage === 'Invoices' && (
          <section className="panel">
            <div className="panel-header">
              <h3>Invoices</h3>
              <input
                type="search"
                value={invoiceSearch}
                onChange={(e) => setInvoiceSearch(e.target.value)}
                placeholder="Search invoices"
              />
            </div>
            <table>
              <thead>
                <tr>
                  <th>Invoice ID</th>
                  <th>Customer</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {invoices.items.length ? (
                  invoices.items.map((invoice) => (
                    <tr key={invoice.id}>
                      <td>{invoice.id}</td>
                      <td>{invoice.customer_id}</td>
                      <td>{formatCurrency(invoice.amount || 0, invoice.currency_code)}</td>
                      <td><span className={`badge status-${invoice.status || 'unknown'}`}>{invoice.status || 'N/A'}</span></td>
                      <td>{formatDate(invoice.date)}</td>
                    </tr>
                  ))
                ) : (
                  <tr><td colSpan="5">No invoices found.</td></tr>
                )}
              </tbody>
            </table>
            <div className="pagination">
              <button onClick={() => loadInvoices(Math.max(1, invoices.page - 1), invoiceSearch)} disabled={invoices.page <= 1}>Previous</button>
              <span>Page {invoices.page}</span>
              <button onClick={() => loadInvoices(invoices.page + 1, invoiceSearch)}>Next</button>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function formatCurrency(value, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function formatDate(value) {
  if (!value) return 'N/A';
  const numeric = Number(value);
  if (Number.isNaN(numeric)) return value;
  const date = new Date(numeric * 1000);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

export default App;
