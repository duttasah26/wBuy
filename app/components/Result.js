const Result = () => {
    return (
        <>
            <div className="w-full m-10 mx-auto text-white rounded-lg shadow-lg overflow-hidden flex border">
                <div className="w-1/3">
                    <img src="https://i.pravatar.cc/300" alt="Card image" class="w-50 h-50 object-cover"/>
                </div>

                <div class="w-2/3 p-4">
                    <h3 class="text-lg font-semibold mb-2">Result</h3>
                    <div class="text-sm text-gray-500">
                        <p class="mb-1">Category 1: <span class="font-medium text-white">Data 1</span></p>
                        <p class="mb-1">Category 2: <span class="font-medium text-white">Data 2</span></p>
                        <p class="mb-1">Category 3: <span class="font-medium text-white">Data 3</span></p>
                    </div>
                </div>
            </div>
        </>
    )
}

export default Result;