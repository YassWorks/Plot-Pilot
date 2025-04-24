import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "Plot Pilot",
    description: "Your AI-powered data visualization assistant",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body>{children}</body>
        </html>
    );
}
