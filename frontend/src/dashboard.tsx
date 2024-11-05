import "./assets/dashboard.css";
import { LineChart, Line, BarChart, Bar, ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip, Label } from 'recharts';

function Dashboard() {

    const userActivity = [
  { date: "Monday", beamBrakes: 120 },
  { date: "Tuesday", beamBrakes: 200 },
  { date: "Wednesday", beamBrakes: 150 },
  { date: "Thursday", beamBrakes: 170 },
  { date: "Friday", beamBrakes: 180 },
  { date: "Saturday", beamBrakes: 220 },
  { date: "Sunday", beamBrakes: 240 }
];


    return (
        
        <div id="Dashboard">
            <div id="Main-Section">
                <div id="All-Charts-Container">
                    <div className="Chart-Container">
                    <ResponsiveContainer height={"100%"} width={"100%"}>
                        <LineChart data={userActivity} margin={{left: 10, bottom: 10}}>
                            <Tooltip />
                            <Line dataKey="beamBrakes" fill="#8874d8" />
                            <CartesianGrid stroke="#ccc" />
                            <XAxis label="Day" />
                            <YAxis>
                                <Label value="Traffic" angle={-90} />
                            </YAxis>
                        </LineChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="Chart-Container">
                    <h3>304</h3>
                    <p>Total Beam Breaks</p>
                    </div>
                    <div className="Chart-Container">
                        <ResponsiveContainer height={"100%"} width={"100%"}>
                            <BarChart data={userActivity}>
                                <Tooltip />
                                <Bar dataKey="beamBrakes" fill="#8874d8" />
                                <XAxis label="Day" />
                                <YAxis>
                                    <Label value="Traffic" angle={-90} />
                                </YAxis>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="Chart-Container">
                        <h3>56</h3>
                        <p>Avg. Daily Beam Breaks</p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Dashboard;
