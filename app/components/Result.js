const Result = () => {
    return (
        <>
            <div className="w-6xl m-10 mx-auto text-white rounded-lg shadow-lg overflow-hidden flex border">
                <div className="w-1/3">
                    <img src="https://avatar.iran.liara.run/public" alt="Card image" class="w-40 h-40 object-cover"/>
                </div>

                <div className="w-2/3 p-4">
                    <h3 className="text-lg font-semibold mb-2">Result</h3>
                    <div className="text-sm text-gray-500">
                        <p className="mb-1">Category 1: <span className="font-medium text-white">Data 1</span></p>
                        <p className="mb-1">Category 2: <span className="font-medium text-white">Data 2</span></p>
                        <p className="mb-1">Category 3: <span className="font-medium text-white">Data 3</span></p>
                    </div>
                </div>
            </div>
        </>
    )
}

export default Result;