"use client";

import { useState, useRef } from "react";
import Image from "next/image";

export default function Home() {
    const [prompt, setPrompt] = useState<string>("");
    const [file, setFile] = useState<FileList | null>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const handleSubmit = async () => {
        if (!file || file.length === 0) {
            alert("Please upload a file.");
            return;
        }

        const formData = new FormData();
        formData.append("prompt", prompt);
        formData.append("file", file[0]);

        try {
            const res = await fetch("http://localhost:5000/plot", {
                method: "POST",
                body: formData,
            });

            if (!res.ok) throw new Error("Upload failed");
            const data = await res.json();
            console.log("Response:", data);
            alert("Data sent to backend successfully!");
        } catch (err) {
            console.error(err);
            alert("Something went wrong!");
        }
    };

    const handleClick = () => {
        inputRef.current?.click();
    };

    const getFile = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFiles = e.target.files;
        setFile(selectedFiles);
    };

    return (
        <div className="px-3 py-40 text-center">
            <div className="py-4 text-4xl font-bold">Plot Pilot</div>

            <div className="relative w-full max-w-lg mx-auto">
                <textarea
                    placeholder="What do you want to plot today?"
                    className="w-full p-4 pr-12 rounded-md bg-gradient-to-br from-stone-900 to-black text-white placeholder-grey-400 resize-none focus:outline-none"
                    rows={4}
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                ></textarea>

                <button
                    onClick={handleSubmit}
                    className="absolute top-4 right-4 z-10 bg-transparent hover:rotate-45 hover:scale-130 transition-transform cursor-pointer"
                >
                    <Image
                        src="/submit.png"
                        alt="submit"
                        height={17}
                        width={17}
                    />
                </button>
            </div>

            <div className="py-4 flex flex-col items-center space-y-4">
                <div className="flex items-center space-x-4">
                    <label className="text-white font-bold">
                        Select your data
                    </label>
                    <input
                        type="file"
                        accept=".csv, .xlsx, .xls"
                        className="hidden"
                        onChange={getFile}
                        ref={inputRef}
                    />
                    <button
                        type="submit"
                        className="px-4 py-2 bg-gradient-to-br from-stone-900 to-black text-white rounded-md transition-shadow shadow-md cursor-pointer hover:scale-110 transition-transform"
                        onClick={handleClick}
                    >
                        <Image
                            src="/upload.png"
                            alt="upload"
                            height="17"
                            width="17"
                        />
                    </button>
                </div>
            </div>
        </div>
    );
}
