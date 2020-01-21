<?php 
include 'dvastnavbar.php';
?>

<!doctype html>
<html lang="en">

<head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
        integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <!-- css -->
    <link rel="stylesheet" href="static/style.css" />
    <!--End css -->
    <title>Home Page</title>
</head>

<body>
    <div class="container"style="text-align:center;">
        <br />
        <div class="bluetop">
            <h4 style="margin-bottom:2%;">Forecasting and Scheduling </h4>
            <form method="POST" action="#">
                <div class="row">
                    <div class="col">
                        <h5>Upload Load File (.xlsx) </h5>
                    </div>
                    <div class="col" >
                        <h5>Growth Parameters </h5>
                    </div>
                    
                </div>    
                <div class="row">
                    <div class="col">
                        (Load Data, Generating Stations, Hydro profile, Solar profile, Wind profile, Nuclear profile) <br><br>
                        <input type="file" name="datafile" multiple>
                    </div>
                    <div class="col" >
                        Enter Load Growth Rate: <input type="number" name="load">%<br>
                        Enter Solar Growth Rate: <input type="number" name="solar">%<br>
                        Enter Wind Growth Rate: <input type="number" name="wind">%<br>
                        Number of years:<input type="number" name="year"><br><br>
                        <input type="submit" class="btn btn-sm btn-primary" name="submit" value="Submit">
                    </div>
                    
                </div>
                <div class = "buttonHolder">
                    <button type="button" class="btn btn-primary btn-lg btn-block" onclick=" window.location.href='/Deloitte/graph_try1.php';">Forecast and Schedule</button>
                      
                    <a href ="#">Results </a>
                </div>
            </form>
        </div>
        <br />
        <div class="greentop">
            <h4 style="margin-bottom:2%;">Analysing Benefits from BESS</h4>
            <div class="row-centered">
                <h5>Bess Parameters</h5>
            </div>  
            <form method="POST" action="#">  
                <div class="row">
                    <div class="col">
                        Life: <input type="number" name="life"> years<br>
                        Discharge period: <input type="number" name="hour"> hours<br>
                        Constant Throughput (1-yes / 0-no): <input type="number" name="throuhput"> hours<br>
                        If constant Throughput, rate of reduction in BESS cost: <input type="number" name="cost_redn"> hours%<br>
                    </div>
                    <div class="col" >
                        Total number of cycles: <input type="number" name="cycles"><br>
                        Round-trip efficiency: <input type="number" name="rt_efficiency">%<br>
                        Degradation Rate: <input type="number" name="degr"><br>
                        Scrap value as percent of initial cost:<input type="number" name="scrap">%
                    </div>
                    <div class="col" >
                        Cost: <input type="number" name="cost"> / MW<br>
                        Depth of discharge <br>
                        <emsp>Upper limit: <input type="number" name="ul">%<br>
                        <emsp>Lower limit: <input type="number" name="ll">%<br>
                    </div> 
                </div>
                <div class = "buttonHolder">
                    <input type="submit" class="btn btn-sm btn-primary" name="submit" value="Submit"><br>
                </div>
            </form>
            <div class="row-centered">
                <h5>Bess Range</h5>
            </div>  
            <form method="POST" action="#">  
                <div class="row">
                    <div class="col">
                        Start size: <input type="number" name="start"> MW<br>
                    </div>
                    <div class="col" >
                        End size: <input type="number" name="end"> MW<br>
                    </div>
                    <div class="col" >
                        Increment size: <input type="number" name="incr"> MW<br>
                    </div> 
                </div>
                <div class="row-centered">
                    <h5>Energy Costs</h5>
                </div>    
                <div class="row">
                    <div class="col">
                        Charging Costs <br>
                        Morning: <input type="number" name="morn"> /kWh<br>
                        Evening: <input type="number" name="even"> /kWh<br>
                    </div>
                    <div class="col" >
                        DSM Price (evening): <input type="number" name="dsm"> /kWh<br>
                        Cost of costliest owned generation: <input type="number" name="peak"> /kWh<br>
                    </div>
                    <div class="col" >
                        Rate of y-o-y increase in energy costs: <input type="number" name="ecr">%<br>
                    </div> 
                </div>
                <div class = "buttonHolder">
                    <input type="submit" class="btn btn-sm btn-primary" name="submit" value="Submit"><br>
                </div>
            </form>
            <div class="row-centered">
                <h5>Financial Parameters</h5>
            </div>  
            <form method="POST" action="#">  
                <div class="row">
                    <div class="col">
                        Loan Percent: <input type="number" name="loan">%<br>
                        Interest Rate: <input type="number" name="interest">%<br>
                    </div>
                    <div class="col" >
                        Tax Rate: <input type="number" name="tax">%<br>
                        Post-tax RoE: <input type="number" name="roe">%<br>
                    </div>
                    <div class="col" >
                        Discount Rate: <input type="number" name="discount">%<br>
                        Operating Expense: <input type="number" name="opex">%<br>
                    </div> 
                </div>
                <div class = "buttonHolder">
                    <input type="submit" class="btn btn-sm btn-primary" name="submit" value="Submit"><br>
                </div>
            </form>
            <div class="row-centered">
                <h5>Other Benefits</h5>
            </div>    
            <form method="POST" action="#">
                <div class="row">
                    <div class="col">
                        <h5>Capacity Deferral</h5>
                        <div class="row">
                            <div class="col">
                                Transformer Cost: <input type="number" name="trans_cost"><br>
                                Transformer interest <input type="number" name="trans_int">%<br>
                            </div>
                            <div class="col">
                                Land cost: <input type="number" name="land_cost">%<br>
                                Transformer Land required: <input type="number" name="land_req">%<br>
                            </div>
                        </div>
                    </div>
                    <div class="col" >
                        <h5>Outage Reduction</h5>
                        No of hours of outage: <input type="number" name="outage">%<br>
                        Average tariff: <input type="number" name="tariff"> /kWh<br>
                    </div>
                    <div class="col" >
                        <h5>Transmission Reductionn</h5>
                        Transmission reduction savings:: <input type="number" name="trans_save"><br>
                    </div> 
                </div>
                <div class = "buttonHolder">
                    <input type="submit" class="btn btn-sm btn-primary" name="submit" value="Submit"><br>
                </div>
            </form>
            <div class = "buttonHolder">
                <button type="button" class="btn btn-primary btn-lg btn-block">Analysis</button>
                <a href ="#">Results </a>
        </div>
    </div>

    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"
        integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous">
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"
        integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous">
    </script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"
        integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous">
    </script>
</body>

</html>