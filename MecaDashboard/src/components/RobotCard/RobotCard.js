import robot from './imgs/robotic-arm.png'
import styles from './RobotCard.module.css'
import React, { useState, useEffect } from 'react'
import StatusBar from '../StatusBar/StatusBar'

export default function RobotCard(props) {
    const [robotState, setRobotState] = useState({
        "Connection": true,
        "Activated": false,
        "Homed": false,
        "Error": false,
    })


    useEffect(() => {
        if (props.connect) {
            const interval = setInterval(async () => {
                const response = await fetch(`/getStatus?ip=${props.ipaddress}`)
                const status = await response.json()
                setRobotState(prevRobotState => {
                    return {
                        'Connection': true,
                        'Activated': status.Activated,
                        'Homed': status.Homed,
                        'Error': status.Error,
                    }
                })
            }, 1000)
        }
    }, [])

    function removeCard() {
        props.deleteCard(props.ipaddress)
    }


    return (
        <div className={styles.robotcard}>
            <button className={styles.closebutton} onClick={removeCard}>X</button>
            <div className={styles.titles}>
                <h1 className={styles.title}>
                    {props.name}
                </h1>
                <a href={`http://${props.ipaddress}`} target='_blank' className={styles.ipaddress}>{props.ipaddress}</a>
            </div>
            {/* <button onClick={onClickHandle}>Click me</button> */}
            <img src={robot} alt='Robot Logo' className={styles.robotlogo}></img>
            <StatusBar robotState={robotState} />
        </div>
    )
}
