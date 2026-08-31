import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#a855f7', '#06b6d4', '#ef4444']

export default function ActionTypeChart({ data }) {
  if (!data) return null

  const chartData = Object.entries(data).map(([type, stats]) => ({
    name: type.replace(/_/g, ' '),
    value: stats.processed,
    recovered: stats.recovered,
    failed: stats.processed - stats.recovered,
  }))

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null
    const d = payload[0].payload
    return (
      <div style={{
        background: '#1e293b', border: '1px solid #334155', borderRadius: 8,
        padding: '12px 16px', color: '#f1f5f9', fontSize: '0.85rem'
      }}>
        <div style={{ fontWeight: 700, marginBottom: 4 }}>{d.name}</div>
        <div>Total: {d.value}</div>
        <div style={{ color: '#22c55e' }}>Recovered: {d.recovered}</div>
        <div style={{ color: '#ef4444' }}>Failed: {d.failed}</div>
      </div>
    )
  }

  return (
    <div className="chart-card">
      <h3>Actions by Type</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={3}
            dataKey="value"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            labelLine={{ stroke: '#64748b' }}
          >
            {chartData.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
