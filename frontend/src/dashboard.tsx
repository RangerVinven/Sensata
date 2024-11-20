import { useState } from "react";

import "./assets/dashboard.css";
import SensorType from "./assets/SensorType.tsx";

import { Select } from "@chakra-ui/react";
import Navbar from "./components/Navbar";
import LineChartComponent from "./components/dashboard/LineChart";
import BarChartComponent from "./components/dashboard/BarChart";
import SensorSelect from "./components/dashboard/SensorSelect";
import { useEffect } from "react";

function Dashboard() {
    // The sensor data
    const [sensor_data, setSensorData] = useState<Array<SensorData>>([]);
    const [totalDailyTraffic, setTotalDailyTraffic] = useState<Number | null>(null);
    const [todaysTraffic, setTodaysTraffic] = useState<Array<SensorData> | null>(null);
    const [pastSevenDaysTraffic, setPastSevenDaysTraffic] = useState<Array<SensorData> | null>(null);
    const [averagePastSevenDaysTraffic, setAveragePastSevenDaysTraffic] = useState<Number | null>(null);
    const [sensors, setSensors] = useState<Array<SensorType> | null>(null)

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
            const response = await fetch("https://idp_api.arfff.dog/api/v1/all_sensors");
            const sensors_json = await response.json();

            setSensors(sensors_json)
            return sensors_json

        } catch (error: any) {
            console.error(error.message)
        }
    }

    // Gets the sensor data for the given sensor
    async function getSensorData(sensor_id: Number) {
        try {
            const response = await fetch(`http://idp_api.arfff.dog/api/v1/sensor_data/${sensor_id}`);
            const response_json = await response.json()

            // Saves the sensor data, and updates today's traffic
            setSensorData(response_json.data)
            return response_json.data;

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

    // Calls the relevant functions to get the sensors and their data
    async function loadDashboard(sensor_index: number = 0) {
        // Gets all the sensors
        const sensors_json = await getSensors();

        // Saves the list in the sensors variable
        setSensors(sensors_json)

        // Gets the data for the first sensor (the default sensor)
        if(sensors_json.length > 0) {
            // Add "No sensors" message
        }

        // Gets the sensor data of sensors[sensor_index], or the first sensor if sensor_index isn't provided
        const sensor_data = await getSensorData(sensors_json?.[sensor_index].sensor_id);

        // Gets the different information to display on the dashboard
        getTodaysTraffic(sensor_data)
        getTrafficFromSevenDays(sensor_data);
        getDailyAverageTraffic(sensor_data);

        setIsLoading(false);
    }

    useEffect(() => {
        loadDashboard()
    }, []);


    return (
        
        <div id="Dashboard">
            <Navbar />

            <div id="Main-Section">
                {
                    isLoading
                    ? <h3>Loading</h3> :
                <div id="Charts-Select-Container">
                    <SensorSelect sensors={sensors} setIsLoading={setIsLoading} />
                    <div id="All-Charts-Container">
                        <div className="Chart-Container">
                            <LineChartComponent pastSevenDaysTraffic={pastSevenDaysTraffic} />
                        </div>
                        <div className="Chart-Container">
                            <h3>{totalDailyTraffic?.toString()}</h3>
                            <p>Today's Total Traffic</p>
                        </div>

                        <div className="Chart-Container">
                            <BarChartComponent todaysTraffic={todaysTraffic} />
                        </div>
                        <div className="Chart-Container">
                            <h3>{averagePastSevenDaysTraffic?.toString()}</h3>
                            <p>Avg. Daily Traffic</p>
                            <p>(Per The Past 7 Days)</p>
                        </div>
                    </div>
                </div>
                }
            </div>
        </div>
    )
}

export default Dashboard;
