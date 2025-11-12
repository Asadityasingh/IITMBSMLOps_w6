-- wrk_iris_predict.lua
-- POST request script for Iris Classification API

wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"

-- Sample Iris flower measurements for testing
local iris_samples = {
    '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}',
    '{"sepal_length": 6.7, "sepal_width": 3.0, "petal_length": 5.2, "petal_width": 2.3}',
    '{"sepal_length": 7.2, "sepal_width": 3.6, "petal_length": 6.1, "petal_width": 2.5}',
    '{"sepal_length": 4.9, "sepal_width": 3.0, "petal_length": 1.4, "petal_width": 0.2}',
    '{"sepal_length": 5.8, "sepal_width": 2.7, "petal_length": 5.1, "petal_width": 1.9}'
}

local counter = 1

request = function()
    local body = iris_samples[counter]
    counter = counter + 1
    if counter > #iris_samples then
        counter = 1
    end
    return wrk.format("POST", nil, nil, body)
end

response = function(status, headers, body)
    if status ~= 200 then
        print("Error: " .. status .. " - " .. body)
    end
end

done = function(summary, latency, requests)
    io.write("------------------------------\n")
    io.write("📊 Stress Test Summary\n")
    io.write("------------------------------\n")
    io.write(string.format("  Total Requests: %d\n", summary.requests))
    io.write(string.format("  Duration: %.2fs\n", summary.duration / 1000000))
    io.write(string.format("  Req/sec: %.2f\n", summary.requests / (summary.duration / 1000000)))
    io.write(string.format("  Transfer: %.2f MB\n", summary.bytes / 1024 / 1024))
    io.write(string.format("  Errors: %d\n", summary.errors.connect + summary.errors.read + summary.errors.write + summary.errors.timeout))
    io.write("------------------------------\n")
    io.write("Latency Percentiles:\n")
    io.write(string.format("  50%%: %.2f ms\n", latency:percentile(50.0) / 1000))
    io.write(string.format("  75%%: %.2f ms\n", latency:percentile(75.0) / 1000))
    io.write(string.format("  90%%: %.2f ms\n", latency:percentile(90.0) / 1000))
    io.write(string.format("  99%%: %.2f ms\n", latency:percentile(99.0) / 1000))
    io.write("------------------------------\n")
end
