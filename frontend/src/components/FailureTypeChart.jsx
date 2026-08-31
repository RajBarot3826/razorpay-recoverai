import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export default function FailureTypeChart({ data }) {
  if (!data) return null

  const chartData = Object.entries(data)
    .map(([type, stats]) => ({
      name: type.replace(/_/g, ' '),
      recovered: stats.recovered,
      failed: stats.processed - stats.recovered,
      total: stats.processed,
      rate: stats.processed > 0 ? ((stats.recovered / stats.processed) * 100).toFixed(0) : 0,
    }))
    .sort((a, b) => b.rate - a.rate)

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null
    const d = payload[0].payload
    return (
      <div style={{
        background: '#1e293b', border: '1px solid #334155', borderRadius: 8,
        padding: '12px 16px', color: '#f1f5f9', fontSize: '0.85rem'
      }}>
        <div style={{ fontWeight: 700, marginBottom: 4 }}>{d.name}</div>
        <div style={{ color: '#22c55e' }}>Recovered: {d.recovered}</div>
        <div style={{ color: '#ef4444' }}>Failed: {d.failed}</div>
        <div style={{ color: '#94a3b8' }}>Rate: {d.rate}%</div>
      </div>
    )
  }

  return (
    <div className="chart-card">
      <h3>Recovery by Failure Type</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis type="number" stroke="#64748b" />
          <YAxis dataKey="name" type="category" width={130} stroke="#64748b" fontSize={11} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="recovered" stackId="a" fill="#22c55e" radius={[0, 0, 0, 0]} />
          <Bar dataKey="failed" stackId="a" fill="#ef4444" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
