import { useEffect, useState } from 'react';
import './App.css';
import API_BASE_URL from "./config"
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons';

function App() {
  const [formData, setFormData] = useState({
    username: '',
    uname: '',
    password: ''
  });

  const [trends, setTrends] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);


  useEffect(() => {
    fetchTopics();
  }, []);

  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData(prev => ({ ...prev, [id]: value }));
  };

  const fetchTopics = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/fetchtopic`);
      const data = await response.json();

      if (response.ok) {
        setTrends(data.data || []);
      } else {
        setError("Failed to fetch trends.");
      }
    } catch (err) {
      setError("Error fetching data.");
    } finally {
      setLoading(false);
    }
  };

  const runscripts = async () => {
    const { username, uname, password } = formData;
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/runscript?username=${encodeURIComponent(username)}&uname=${encodeURIComponent(uname)}&password=${encodeURIComponent(password)}`);
      const result = await response.json();

      if (response.ok) {
        alert("Trending topics fetched successfully.");
        fetchTopics();
        setFormData({ username: '', uname: '', password: '' });
      } else {
        setError("Script failed: " + result.error);
      }
    } catch (err) {
      setError("Error running script.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 className='title'>Enter Twitter Details</h1>
      <form onSubmit={(e) => e.preventDefault()}>
        <label>
          Username:
          <input type="text" id="username" value={formData.username} onChange={handleChange} required />
        </label><br /><br />
        <label>
          Uname:
          <input type="text" id="uname" value={formData.uname} onChange={handleChange} required />
        </label><br /><br />
        <label style={{ position: 'relative', display: 'block' }}>
          Password:
          <input
            type={showPassword ? 'text' : 'password'}
            id="password"
            value={formData.password}
            onChange={handleChange}
            required
            style={{ paddingRight: '40px' }}
          />
          <span
            onClick={() => setShowPassword(prev => !prev)}
            style={{
              position: 'absolute',
              right: '10px',
              top: '55%',
              transform: 'translateY(-50%)',
              cursor: 'pointer',
              fontSize: '1.2rem',
              color: '#888'
            }}
          >
            <FontAwesomeIcon icon={showPassword ? faEyeSlash : faEye} />
          </span>
        </label>

        <button type="button" onClick={runscripts} disabled={loading}>Save & Run Script</button>
        {loading && <p>Loading...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </form><br />

      <div id="trends">
        {trends.length > 0 ? (
          <>
            <h3>Latest Trending Topics:</h3>
            <div className="trend-cards">
              <div className="trend-card">
                <ul>
                  <li><strong>1) </strong> {trends[trends.length - 1].Trend1}</li>
                  <li><strong>2) </strong> {trends[trends.length - 1].Trend2}</li>
                  <li><strong>3) </strong> {trends[trends.length - 1].Trend3}</li>
                  <li><strong>4) </strong> {trends[trends.length - 1].Trend4}</li>
                  <li><strong>5) </strong> {trends[trends.length - 1].Trend5}</li>
                  <li><strong>IP:</strong> {trends[trends.length - 1].IP}</li>
                  <li><strong>Date:</strong> {new Date(trends[trends.length - 1].Date).toLocaleString()}</li>
                </ul>
              </div>
            </div>
          </>
        ) : (
          <p>No trends available.</p>
        )}
      </div>

      <div id="trends">
        {trends.length > 0 ? (
          <>
            <h3>Old Trending Topics:</h3>
            <div className="trend-cards">
              {trends.slice(0, trends.length - 1).map((trend, index) => (
                <div key={index} className="trend-card">
                  <ul>
                    <li><strong>1) </strong> {trend.Trend1}</li>
                    <li><strong>2) </strong> {trend.Trend2}</li>
                    <li><strong>3) </strong> {trend.Trend3}</li>
                    <li><strong>4) </strong> {trend.Trend4}</li>
                    <li><strong>5) </strong> {trend.Trend5}</li>
                    <li><strong>IP:</strong> {trend.IP}</li>
                    <li><strong>Date:</strong> {new Date(trend.Date).toLocaleString()}</li>
                  </ul>
                </div>
              ))}
            </div>
          </>
        ) : (
          <p>No trends available.</p>
        )}
      </div>


    </div>
  );
}

export default App;
