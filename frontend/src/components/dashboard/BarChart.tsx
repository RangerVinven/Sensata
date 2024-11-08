import { useState, useEffect } from "react";
import { Legend, BarChart, Bar, ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';

function BarChartComponent(props: any) {

    const [todaysTrafficFromProps, setTodaysTrafficFromProps] = useState<Array<SensorData> | null>(props.todaysTraffic)
    const [todaysTraffic, setTodaysTraffic ] = useState<Array<Object> | null>(null);

    type SensorData = {
        time_added: string,
        sensor_id_sensor_table: Number,
        time_recorded: string,
        sensor_data_id: Number,
        unique_id: string,
        data: string
    }

    type FormattedData = {
        "name": string,
        "Traffic": number
    }

    function formatTimes(traffic: any) {
        let formattedTime = [] 
        let timesTrafficMap: any = {}

        // Populates the timesTrafficMap
        for (let i = 0; i < traffic.length; i++) {
            const time_recorded = new Date(traffic[i].time_recorded);
            time_recorded.setMinutes(0, 0, 0) // Sets the minutes to 0

            const hour = time_recorded.getHours();

            if(hour in timesTrafficMap) {
                timesTrafficMap[hour] += 1;
            } else {
                timesTrafficMap[hour] = 1;
            }
        }

        // Fills in the formattedTime
        for (let key in timesTrafficMap) {
            formattedTime.push({
                "name": key,
                "Traffic": timesTrafficMap[key]
            })
        }

        setTodaysTraffic(formattedTime)
    }

    useEffect(() => {
        console.log(props.todaysTraffic)
        formatTimes(props.todaysTraffic);
    }, [])

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

    if(todaysTraffic === null) {
        return <h3>Loading...</h3>
    } else {
        return <ResponsiveContainer height={"100%"} width={"100%"}>
            <BarChart data={todaysTraffic}>
                <CartesianGrid />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Traffic" fill="#BF40BF" />
            </BarChart>
        </ResponsiveContainer>
    }
}

export default BarChartComponent;
