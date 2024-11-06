import "./assets/dashboard.css";
import { LineChart, Line, Legend, BarChart, Bar, ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip, Label } from 'recharts';

function Dashboard() {

    const weeklyActivity = [
  { day: "Mon", "Traffic": 120 },
  { day: "Tue", "Traffic": 200 },
  { day: "Wed", "Traffic": 150 },
  { day: "Thu", "Traffic": 170 },
  { day: "Fri", "Traffic": 180 },
  { day: "Sat", "Traffic": 220 },
  { day: "Sun", "Traffic": 240 }
];

const hourlyData = [
  { "name": "12am", "Traffic": 120 },
  { "name": "1am", "Traffic": 90 },
  { "name": "2am", "Traffic": 75 },
  { "name": "3am", "Traffic": 60 },
  { "name": "4am", "Traffic": 50 },
  { "name": "5am", "Traffic": 45 },
  { "name": "6am", "Traffic": 70 },
  { "name": "7am", "Traffic": 85 },
  { "name": "8am", "Traffic": 100 },
  { "name": "9am", "Traffic": 150 },
  { "name": "10am", "Traffic": 180 },
  { "name": "11am", "Traffic": 200 },
  { "name": "12pm", "Traffic": 220 },
  { "name": "1pm", "Traffic": 210 },
  { "name": "2pm", "Traffic": 230 },
  { "name": "3pm", "Traffic": 240 },
  { "name": "4pm", "Traffic": 250 },
  { "name": "5pm", "Traffic": 260 },
  { "name": "6pm", "Traffic": 270 },
  { "name": "7pm", "Traffic": 260 },
  { "name": "8pm", "Traffic": 240 },
  { "name": "9pm", "Traffic": 220 },
  { "name": "10pm", "Traffic": 190 },
  { "name": "11pm", "Traffic": 160 }
];

    return (
        
        <div id="Dashboard">
            <div id="Main-Section">
                <div id="All-Charts-Container">
                    <div className="Chart-Container">
                    <ResponsiveContainer height={"100%"} width={"100%"}>
                        <LineChart data={weeklyActivity}>
                            <CartesianGrid />
                            <XAxis dataKey="day" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line dataKey="Traffic" fill="#BF40BF" />
                        </LineChart>
                    </ResponsiveContainer>
                    </div>
                    <div className="Chart-Container">
                        <h3>206</h3>
                        <p>Today's Total Traffic</p>
                    </div>

                    <div className="Chart-Container">
                    <ResponsiveContainer height={"100%"} width={"100%"}>
                        <BarChart data={hourlyData}>
                            <CartesianGrid />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="Traffic" fill="#BF40BF" />
                        </BarChart>
                    </ResponsiveContainer>
                    </div>
                    <div className="Chart-Container">
                        <h3>56</h3>
                        <p>Avg. Daily Traffic</p>
                        <p>(Per The Past 7 Days)</p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Dashboard;
