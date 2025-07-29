import React from 'react'
import styles from './StatusLed.module.css'

export default function StatusLed(props) {
    return (
        <div className={`${styles.led} ${styles[props.bgcolor]}`}></ div>
    )
}
