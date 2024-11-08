import { useState, useEffect } from "react"
import { LineChart, Line, Legend, ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';

function LineChartComponent(props: any) {

    const [pastSevenDaysTraffic, setPastSevenDaysTraffic] = useState(props.pastSevenDaysTraffic); // The raw past 7 days traffic
    const [weeklyTraffic, setWeeklyTraffic] = useState<Array<WeekDayData> | null>(null) // The formatted traffic from the past 7 days

    type WeekDayData = {
        day: string,
        Traffic: number
    }

    type WeekDays = {
        Mon: Number,
        Tue: Number,
        Wed: Number,
        Thu: Number,
        Fri: Number,
        Sat: Number,
        Sun: Number
    }

    type SensorData = {
        time_added: string,
        sensor_id_sensor_table: Number,
        time_recorded: string,
        sensor_data_id: Number,
        unique_id: string,
        data: string
    }

    // Converts the numbers 0-6 to "Mon" - "Sun"
    function convertDayToDayName(day: number) : string {
        if (day > 6 || day < 0) throw new Error("Number must be between 0 and 6");

        switch(day) {
            case 0:
                return "Sun"
            case 1:
                return "Mon"
            case 2:
                return "Tue"
            case 3:
                return "Wed"
            case 4:
                return "Thu"
            case 5:
                return "Fri"
            case 6:
                return "Sat"
        }

        return "";
    }

    // Adds the missing days where there wasn't traffic, to the given object
    function addRestOfDaysToArray(days: WeekDays) {
        const weekDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for (let i = 0; i < weekDays.length; i++) {
            if (!(weekDays[i] in days)) {
                days[weekDays[i] as keyof WeekDays] = 0;
            }
        }

        return days;
    }

    function convertDayToNumber(day: string) {
        switch(day) {
            case "Sun":
                return 0
            case "Mon":
                return 1
            case "Tue":
                return 2
            case "Wed":
                return 3
            case "Thu":
                return 4
            case "Fri":
                return 5
            case "Sat":
                return 6

        }
        return 1
    }

    function parseTraffic(traffic: Array<SensorData>) {

        let trafficPerDay: any = {}

        // Loops over the traffic
        for (let i = 0; i < traffic.length; i++) {
            const time_recorded = new Date(traffic[i].time_recorded);
            const time_day = time_recorded.getDay() // Returns 0-6 ("Monday"-"Sunday")

            // Adds the day to the trafficPerDay
            if(convertDayToDayName(time_day) in trafficPerDay) {
                trafficPerDay[convertDayToDayName(time_day)] += 1;
            } else {
                trafficPerDay[convertDayToDayName(time_day)] = 1;
            }
        }


        // Adds the remaning days and sets them to 0
        // trafficPerDay = addRestOfDaysToArray(trafficPerDay);

        // Turns the traffic into an array of objects
        let weeklyActivityArray = [];
        for(let key in trafficPerDay) {
            weeklyActivityArray.push({
                day: key,
                "Traffic": trafficPerDay[key]
            })
        }


        const daysOrder = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
        weeklyActivityArray.sort((a: any, b: any) => daysOrder.indexOf(a.day) - daysOrder.indexOf(b.day));

        setWeeklyTraffic(weeklyActivityArray)

    }

    useEffect(() => {
        parseTraffic(pastSevenDaysTraffic)
    }, [])

    const weeklyActivity = [
  { day: "Mon", Traffic: 120 },
  { day: "Tue", Traffic: 200 },
  { day: "Wed", Traffic: 150 },
  { day: "Thu", Traffic: 170 },
  { day: "Fri", Traffic: 180 },
  { day: "Sat", Traffic: 220 },
  { day: "Sun", Traffic: 240 }
];

    if (weeklyTraffic == null) {
        return <h3>Loading...</h3>
    } else {
        return <ResponsiveContainer height={"100%"} width={"100%"}>
            <LineChart data={weeklyTraffic}>
               <CartesianGrid />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line dataKey="Traffic" fill="#BF40BF" />
            </LineChart>
        </ResponsiveContainer>
    }
}

export default LineChartComponent;
