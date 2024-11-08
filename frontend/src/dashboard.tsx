import { useState } from "react";
import "./assets/dashboard.css";

import Navbar from "./components/Navbar";
import LineChartComponent from "./components/dashboard/LineChart";
import BarChartComponent from "./components/dashboard/BarChart";
import { useEffect } from "react";

function Dashboard() {
    // The sensor data
    const [sensor_data, setSensorData] = useState<Array<SensorData>>([]);
    const [totalDailyTraffic, setTotalDailyTraffic] = useState<Number | null>(null);
    const [todaysTraffic, setTodaysTraffic] = useState<Array<SensorData> | null>(null);
    const [pastSevenDaysTraffic, setPastSevenDaysTraffic] = useState<Array<SensorData> | null>(null);
    const [averagePastSevenDaysTraffic, setAveragePastSevenDaysTraffic] = useState<Number | null>(null);

    const [isLoading, setIsLoading] = useState<boolean>(true);

    type SensorData = {
        time_added: string,
        sensor_id_sensor_table: Number,
        time_recorded: string,
        sensor_data_id: Number,
        unique_id: string,
        data: string
    }

    // Gets all the sensors
    async function getSensors() {
        try {
            const response = await fetch("http://localhost:8000/api/v1/all_sensors");
            const sensors = await response.json();

            return sensors

        } catch (error: any) {
            console.error(error.message)
        }
    }

    // Gets the sensor data for the given sensor
    async function getSensorData(sensor_id: Number) {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/${sensor_id}`);
            const sensor_data = JSON.parse(await response.json());

            // Saves the sensor data, and updates today's traffic
            setSensorData(sensor_data)
            getTodaysTraffic(sensor_data)

            return sensor_data;

        } catch (error: any) {
            console.error(error.message)
        }
    }

    // Gets the traffic from today
    function getTodaysTraffic(sensor_data: Array<SensorData>) {
        const todaysTrafficArray = sensor_data.filter(data => {
            // Gets the time recorded and the current time as a Date object
            const time_recorded = new Date(data.time_recorded);
            const today = new Date();

            // Returns true (and adds to the todaysTraffic if the time_recorded is today)
            return (time_recorded.getDate() === today.getDate()) && (time_recorded.getMonth() === today.getMonth()) && (time_recorded.getFullYear() === today.getFullYear())
        })

        // Sets todays traffic and its total
        setTodaysTraffic(todaysTrafficArray);
        setTotalDailyTraffic(todaysTrafficArray.length);

        // Sets the weekly traffic and its total
        getTrafficFromSevenDays(sensor_data);
        getDailyAverageTraffic(sensor_data);

        return todaysTraffic;
    }


    // Gets the traffic from the past 7 days
    function getTrafficFromSevenDays(sensor_data: Array<SensorData>) {
        // Gets today's date
        const today = new Date();
        today.setHours(0, 0, 0, 0); // Stops the time from being an issue

        // Calculates 7 days ago
        const seven_days_ago = new Date(today);
        seven_days_ago.setDate(today.getDate() - 7);

        const pastSevenDays = sensor_data.filter(data => {
            const time_recorded = new Date(data.time_recorded)

            // Returns true if the time recorded is between 7 days ago and today
            return time_recorded >= seven_days_ago && time_recorded <= today
        });

        setPastSevenDaysTraffic(pastSevenDays);
        return pastSevenDays;
    }


    // Gets the average daily traffic from the past 7 days
    function getDailyAverageTraffic(traffic: Array<SensorData>) {
        let trafficPerDay: Record<number, number> = {}

        // Loops over the traffic array, adding the day (0-6 for the days of the week) to the dictionary
        // Results in something like { 2: 3, 4: 9, 5: 5 } (the keys representing "Monday"-"Sunday")
        for (let i = 0; i < traffic.length; i++) {
            const time_recorded = new Date(traffic[i].time_recorded);
            const time_day = time_recorded.getDay() // Returns 0-6 ("Monday"-"Sunday")

            if(time_day in trafficPerDay) {
                trafficPerDay[time_day] += 1;
            } else {
                trafficPerDay[time_day] = 1;
            }
        }

        // Loops over each day's traffic, adding it to the average
        let average = 0;
        for(let key in trafficPerDay) {
            average += trafficPerDay[key]
        }

        // Makes average 0 if there's been no traffic, otherwise sets average to the actual average (this avoids NAN)
        average = average == 0 ? 0 : Math.round(average/Object.keys(trafficPerDay).length)
        setAveragePastSevenDaysTraffic(average)

        return average
    }


    useEffect(() => {
        getSensorData(1);
        setIsLoading(false);
    }, []);

    return (
        
        <div id="Dashboard">
            <Navbar />

            <div id="Main-Section">
                <div id="All-Charts-Container">
                    <div className="Chart-Container">
                    {pastSevenDaysTraffic != null
                     ?  <>
                            <LineChartComponent pastSevenDaysTraffic={pastSevenDaysTraffic} />
                        </>
                    : <h3>Loading...</h3>
                    }
                    </div>
                    <div className="Chart-Container">
                    {totalDailyTraffic != null
                     ?  <>
                            <h3>{totalDailyTraffic.toString()}</h3>
                            <p>Today's Total Traffic</p>
                        </>
                    : <h3>Loading...</h3>
                    }
                    </div>

                    <div className="Chart-Container">
                    {todaysTraffic != null
                     ?  <>
                            <BarChartComponent todaysTraffic={todaysTraffic} />
                        </>
                    : <h3>Loading...</h3>
                    }
                    </div>
                    <div className="Chart-Container">
                        {averagePastSevenDaysTraffic != null
                         ?  <>
                                <h3>{averagePastSevenDaysTraffic.toString()}</h3>
                                <p>Avg. Daily Traffic</p>
                                <p>(Per The Past 7 Days)</p>
                            </>
                        : <h3>Loading...</h3>
                        }
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Dashboard;
