import React, { useState, useEffect } from 'react'

export default function App() {
  const [backendStatus, setBackendStatus] = useState({ state: 'checking', data: null })

  useEffect(() => {
    fetch('/api/')
      .then(res => res.json())
      .then(data => setBackendStatus({ state: 'online', data }))
      .catch(err => setBackendStatus({ state: 'offline', error: err.message }))
  }, [])

  return (
    <div style={{ maxWidth: '850px', margin: '40px auto', padding: '24px', backgroundColor: '#1e293b', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.4)' }}>
      <header style={{ borderBottom: '1px solid #334155', paddingBottom: '16px', marginBottom: '24px' }}>
        <h1 style={{ margin: 0, color: '#38bdf8', fontSize: '2rem' }}>☁️ CloudVault</h1>
        <p style={{ margin: '8px 0 0', color: '#94a3b8' }}>Hệ thống Cloud Data Storage - Đồ án môn Điện toán đám mây</p>
      </header>

      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.2rem', color: '#f1f5f9' }}>Kiểm tra trạng thái kết nối các tầng:</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginTop: '12px' }}>
          
          <div style={{ padding: '16px', backgroundColor: '#0f172a', borderRadius: '8px', borderLeft: '4px solid #38bdf8' }}>
            <strong style={{ color: '#94a3b8' }}>Frontend (React/Vite)</strong>
            <p style={{ margin: '8px 0 0', color: '#4ade80', fontWeight: 'bold' }}>● Đang chạy (Port 3000)</p>
          </div>

          <div style={{ padding: '16px', backgroundColor: '#0f172a', borderRadius: '8px', borderLeft: `4px solid ${backendStatus.state === 'online' ? '#4ade80' : '#ef4444'}` }}>
            <strong style={{ color: '#94a3b8' }}>Backend (FastAPI)</strong>
            <p style={{ margin: '8px 0 0', color: backendStatus.state === 'online' ? '#4ade80' : '#ef4444', fontWeight: 'bold' }}>
              {backendStatus.state === 'online' ? '● Đã kết nối (/api/)' : backendStatus.state === 'checking' ? '○ Đang kiểm tra...' : '✕ Không kết nối'}
            </p>
          </div>

          <div style={{ padding: '16px', backgroundColor: '#0f172a', borderRadius: '8px', borderLeft: '4px solid #a855f7' }}>
            <strong style={{ color: '#94a3b8' }}>Reverse Proxy (Nginx)</strong>
            <p style={{ margin: '8px 0 0', color: '#a855f7', fontWeight: 'bold' }}>● Đón cổng 80</p>
          </div>

        </div>
      </div>

      <div style={{ padding: '16px', backgroundColor: '#0f172a', borderRadius: '8px', marginBottom: '24px' }}>
        <h3 style={{ margin: '0 0 12px', fontSize: '1rem', color: '#f8fafc' }}>Đường dẫn nhanh cho lập trình viên:</h3>
        <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.8' }}>
          <li><a href="/docs" target="_blank" rel="noreferrer" style={{ color: '#38bdf8' }}>API Swagger Docs (/docs)</a></li>
          <li><a href="http://localhost:9001" target="_blank" rel="noreferrer" style={{ color: '#38bdf8' }}>MinIO Storage Console (Port 9001)</a> - User: <code>minioadmin</code> / Pass: <code>miniopassword123</code></li>
        </ul>
      </div>

      <footer style={{ borderTop: '1px solid #334155', paddingTop: '16px', textAlign: 'center', color: '#64748b', fontSize: '0.9rem' }}>
        Bước 4 hoàn tất: Docker Compose đã có đầy đủ skeleton code để cả 3 máy cùng chạy được!
      </footer>
    </div>
  )
}
