import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api, setToken } from '../lib/api';

export default function Register() {
  const [form, setForm] = useState({ full_name: '', email: '', password: '', organization_name: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  function update(field, value) {
    setForm(prev => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const { access_token } = await api.register(form);
      setToken(access_token);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-wrap">
      <form className="card auth-card" onSubmit={handleSubmit}>
        <div className="brand"><span className="brand-mark" />GRC Intelligence</div>
        <h1>Create an Account</h1>
        <p className="subtitle">The first user in your organization automatically gets Admin access</p>

        <label>Full Name</label>
        <input value={form.full_name} onChange={e => update('full_name', e.target.value)} required />

        <label>Organization Name (optional)</label>
        <input value={form.organization_name} onChange={e => update('organization_name', e.target.value)} />

        <label>Email</label>
        <input type="email" value={form.email} onChange={e => update('email', e.target.value)} required />

        <label>Password (min. 8 characters)</label>
        <input type="password" minLength={8} value={form.password} onChange={e => update('password', e.target.value)} required />

        {error && <div className="error-box">{error}</div>}

        <button className="primary" type="submit" disabled={loading} style={{ width: '100%' }}>
          {loading ? 'Creating account...' : 'Create Account'}
        </button>

        <p style={{ marginTop: 18, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--accent-amber)' }}>Log in</Link>
        </p>
      </form>
    </div>
  );
}
