var builder = DistributedApplication.CreateBuilder(args);

var apiService = builder.AddProject<Projects.blazor_trapistan_ApiService>("apiservice");

builder.AddProject<Projects.blazor_trapistan_Web>("webfrontend")
    .WithExternalHttpEndpoints()
    .WithReference(apiService)
    .WaitFor(apiService);

builder.Build().Run();
