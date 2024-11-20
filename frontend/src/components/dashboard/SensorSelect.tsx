import SensorType from "../../assets/SensorType.tsx";
import "../../assets/SensorSelect.css";

type Props = {
    sensors: Array<SensorType> | null,
    setIsLoading: Function
    loadDashboard: Function
}

// The select menu for the sensors
function SensorSelect(props: Props) {

    // Called when the sensor gets changed
    function changeSensor(event: any) {
        props.setIsLoading(true);
        props.loadDashboard(event.target.value);
    }

    return <>
        <select className="dropdown" onChange={e => changeSensor(e)} >
            <option value="" disabled selected>Select a sensor</option>
            {
                props.sensors?.map((sensor, index) => {
                    return <option value={index} selected={index === 0}>{ sensor.sensor_model_name }</option>
                })
            }
        </select>
    </>
}

export default SensorSelect; 

