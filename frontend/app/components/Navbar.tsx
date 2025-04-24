import React from "react";
import Link from "next/link";
import Image from "next/image";

function Navbar() {
    return (
        <div className="px-2 py-2 shadow-xl flex flex-col items-start justify-start h-screen fixed bg-neutral-900">
            <Link href="/" className="py-3"><Image src="/home.png" alt="home" height="17" width="17" /></Link>
            <Link href="/history" className="py-3"><Image src="/history.png" alt="history" height="19" width="19" /></Link>
            <Link href="/contact" className="py-3"><Image src="/mobile.png" alt="mobile" height="21" width="21" /></Link>
            <Link href="/about" className="px-0.5 py-3"><Image src="/information.png" alt="information" height="16" width="16" /></Link>
        </div>
    );
}

export default Navbar;
