import React from 'react'
import styles from './NavBar.module.css'
import lilogo from './imgs/lilogo.png'
import twitterlogo from './imgs/twitterlogo.png'

export default function NavBar() {
    return (
        <div className={styles.navbar}>
            <a href='https://www.mecademic.com/' target="_blank"><img className={styles.logo} src='https://cdn.mecademic.com/uploads/img-tiny/mecademic-logo.png' alt='Logo' /></a>
            <div className={styles.links}>
                <a href='https://www.mecademic.com/en/downloads#meca500-robot-arm' target='_blank'>Documentation</a>
                <a href='https://support.mecademic.com/support/home' target='_blank'>Support</a>
            </div>
            <div className={styles.socials}>
                <a><img className={styles.lilogo} src={lilogo} /></a>
                <a><img className={styles.twitterlogo} src={twitterlogo} /></a>
            </div>
        </div>
    )
}
