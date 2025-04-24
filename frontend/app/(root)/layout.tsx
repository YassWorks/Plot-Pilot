import React from "react";
import Navbar from "~/app/components/Navbar";

function Layout({ children }: { children: React.ReactNode }) {
    return (
        <div>
            <Navbar />
            {children}
        </div>
    );
}

export default Layout;
