import "./assets/dashboard.css";

import Navbar from "./components/Navbar";
import LineChartComponent from "./components/dashboard/LineChart";
import BarChartComponent from "./components/dashboard/BarChart";

function Dashboard() {


    return (
        
        <div id="Dashboard">
            <Navbar />

            <div id="Main-Section">
                <div id="All-Charts-Container">
                    <div className="Chart-Container">
                        <LineChartComponent />
                    </div>
                    <div className="Chart-Container">
                        <h3>206</h3>
                        <p>Today's Total Traffic</p>
                    </div>

                    <div className="Chart-Container">
                        <BarChartComponent />
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
