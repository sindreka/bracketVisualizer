var nations = [];
var attacker;
var victim;
var color;
var reinforcer;
var clickRadius = 40;
var mouseOffsetX = 15;
var mouseOffsetY = - 10;
var atk;
var def;

var player = {
    color : "red",
    troopsDue : 3,
    stage : 1,
    placeTroops : function() {
        if ( this.troopsDue == 0 ) { this.stage = 2; }
        else {
            clicked = click();
            if ( clicked && clicked.owner == this.color ) {
                clicked.troops++;
                this.troopsDue--;
            }
        }
    },
    attack : function () {
        clicked = click();
        if ( clicked ) {
            if ( clicked.canAttack() ) {
                if ( attacker ) { attacker.isAttacking = false; }
                attacker = clicked;
                attacker.isAttacking = true;
            }
            if ( attacker && attacker.canAttack(clicked) ) {
                victim = clicked;
                attacker.assault(victim);
            }

//        if ( atk && def ) { drawDice(atk, def, attacker, victim ); }
//        if ( reinforcer ) { 
//            markNation( reinforcer, "green" );
//            infoAdvance(victim, reinforcer);
//        } else { infoAdvance(); }
//        if ( clicked ) {
//            if ( clicked.owner == this.color ) {
//                if ( reinforcer && victim && victim.owner == reinforcer.owner && victim == clicked ) {
//                    reinforcer.troops--;
//                    victim.troops++;
//                    atk = null;
//                    def = null;
//                    if ( reinforcer.troops < 2 ) { reinforcer = null; }
//                }
//                else if ( clicked.troops > 1 ) { 
//                    attacker = clicked;
//                    reinforcer = null;
//                }
//            }
//            else if ( attacker && ~attacker.borders.indexOf(clicked.id) ) { 
//                victim = clicked;
//                color = victim.owner;
//                attacker.assault(victim); 
//                if ( attacker && attacker.troops <= 1 ) { attacker = null; } 
//            }
//        }
        
        }
    }
}

function startGame() {
    gameBoard = new map(640,400,"maps/first.png");

    nations[0] = new nation("Leftia",0,9,"red",[1,2],78,99);
    nations[1] = new nation("Middletown",1,10,"blue",[0,2,3],208,216);
    nations[2] = new nation("East worth",2,3,"red",[0,1,3],424,160);
    nations[3] = new nation("South right",3,3,"orange",[1,2],368,313);

    myGameArea.start();
}

function nation(name,id,troops,owner,borders,x,y) {
    this.name = name;
    this.id = id;
    this.troops = troops;
    this.owner = owner;
    this.borders = borders;
    this.x = x;
    this.y = y;
    this.isAttacking = false;
    this.assault = function(victim) {
        numAttackers = Math.min(3,this.troops-1);
        numDefenders = Math.min(2,victim.troops);
        atk = dieRoll(numAttackers);
        def = dieRoll(numDefenders);
        //drawDice( atk, def, "blue" );
        if (atk[0] > def[0]) { victim.troops--; }
        else { this.troops--; }
        if (numAttackers > 1 && numDefenders > 1) {
            if (atk[1] > def[1]) { victim.troops--; }
            else { this.troops--; }
        }
        if (victim.troops == 0){
            victim.owner = this.owner;
            victim.troops = 1;
            this.troops--;
            reinforcer = this;
            attacker = null;
        }
    }
    this.canAttack = function(victim) {
        //return false;
        if ( this.troops < 2 || this.owner != player.color ) { return false; }
        for ( i = 0 ; i < this.borders.length ; i++ ) {
            potentialVictim = nations[this.borders[i]];
            if ( potentialVictim.owner != this.owner ) {
                if ( victim == null || potentialVictim == victim ) { return true; }
            }
        } return false;
    }
}

var myGameArea = {
    canvas : document.createElement("canvas"),
    start : function() {
        this.canvas.width = 640;
        this.canvas.height = 450;
        this.context = this.canvas.getContext("2d");
        document.body.insertBefore(this.canvas, document.body.childNodes[0]);
        this.canvas.style.border = "1px solid";
        this.interval = setInterval(updateGameArea, 20);
        window.addEventListener('mousedown', function (e) {
            myGameArea.x = e.pageX;
            myGameArea.y = e.pageY;
        })
        window.addEventListener('mouseup', function (e) {
            myGameArea.x = false;
            myGameArea.y = false;
        })
    },
    clear : function(){
        this.context.clearRect(0,0, this.canvas.width, this.canvas.height);
    }
}

function updateGameArea() {
    myGameArea.clear();
    gameBoard.update();
    updateNations();

    if ( player.stage == 1 ) { player.placeTroops(); }
    if ( player.stage == 2 ) { player.attack(); }

}

function updateNations() {
    for ( i = 0 ; i < nations.length ; i++ ) {
        nation = nations[i];
        drawText( nation.troops, nation.owner, nation.x, nation.y );
        //console.log(nation.canAttack());
        if ( nation.isAttacking && nation.canAttack() == false ) { nation.isAttacking = false; }
        if ( nation.isAttacking ) { 
            markNation( nation, "red" ); 
        }
    }
}


function map(width,height,file) {
    this.image = new Image();
    this.image.src = file;
    this.width = width;
    this.height = height;
    this.update = function() {
        myGameArea.context.drawImage(this.image, 0, 0, this.width, this.height);
    }
}

function drawText(text, color, x, y) {
    myGameArea.context.font = "30px monospace";
    myGameArea.context.fillStyle = color;
    if ( text >= 10 ) {
        x -= 10;
    }
    myGameArea.context.fillText(text, x, y);
}

function dieRoll(num) {
    results = [];
    for (i = 0 ; i < num ; i++) {
        results[i] = Math.floor(Math.random() * 6) + 1;
    }
    return results.sort().reverse();
}

function dist(x1,y1,x2,y2) { 
    return ( x1 - x2 ) ** 2 + ( y1 - y2 ) ** 2;
}

function click() {
    if ( myGameArea.x ) {
        for ( i = 0 ; i < nations.length ; i++ ) {
            if ( dist( nations[i].x,nations[i].y,myGameArea.x - mouseOffsetX,myGameArea.y - mouseOffsetY ) < clickRadius ** 2 ) { 
                myGameArea.x = false;
                myGameArea.y = false;
                return nations[i] }
        }
    }
    return false;
}

function drawDice( atk, def, agressor, victim ) {
    var x = 10;
    var y = gameBoard.height + 5;
    var dieSize = 30;
    drawText(agressor.name, x, y - 15 );
    for (i = 0 ; i < atk.length ; i++ ) {
        if ( def[i] && atk[i] > def[i] ) {
            myGameArea.context.fillStyle = "#666699";
            myGameArea.context.fillRect( x-3, y-3, dieSize + 6, dieSize + 6 );
        }
        drawDie( atk[i], x, y, dieSize, agressor.owner );
        x += dieSize + 10;
    }
    x += 15;
    drawText(victim.name, x, y - 15 );
    for (i = 0 ; i < def.length ; i++ ) {
        if ( atk[i] && def[i] >= atk[i] ) {
            myGameArea.context.fillStyle = "#666699";
            myGameArea.context.fillRect( x-3, y-3, dieSize + 6, dieSize + 6 );
        }
        drawDie( def[i], x, y, dieSize, victim.owner );
        x += dieSize + 10;
    }
}

function drawDie( num, x, y, dieSize, color ) {
    var dotSize = 3.6;
    myGameArea.context.beginPath();
    myGameArea.context.fillStyle = color;
    myGameArea.context.lineWidth = 2;
    myGameArea.context.fillRect(x, y, dieSize, dieSize);
    myGameArea.context.fillStyle = "white";
    if ( num == 1 || num == 3 || num == 5 ) {
        myGameArea.context.fillRect( x + dieSize / 2 - dotSize / 2, y + dieSize / 2 - dotSize / 2, dotSize, dotSize );
    }
    if ( num == 2 || num == 3 ) {
        myGameArea.context.fillRect( x + dieSize / 4 - dotSize / 2, y + dieSize / 4 - dotSize / 2, dotSize, dotSize );
        myGameArea.context.fillRect( x + 3 * dieSize / 4 - dotSize / 2, y + 3 * dieSize / 4 - dotSize / 2, dotSize, dotSize );
    }
    if ( num == 4 || num == 5 || num == 6 ) {
        myGameArea.context.fillRect( x + dieSize / 4 - dotSize / 2, y + dieSize / 4 - dotSize / 2, dotSize, dotSize );
        myGameArea.context.fillRect( x + dieSize / 4 - dotSize / 2, y + 3 * dieSize / 4 - dotSize / 2, dotSize, dotSize );
        myGameArea.context.fillRect( x + 3 * dieSize / 4 - dotSize / 2, y + dieSize / 4 - dotSize / 2, dotSize, dotSize );
        myGameArea.context.fillRect( x + 3 * dieSize / 4 - dotSize / 2, y + 3 * dieSize / 4 - dotSize / 2, dotSize, dotSize );
    }
    if ( num == 6 ) {
        myGameArea.context.fillRect( x + dieSize / 4 - dotSize / 2, y + dieSize / 2 - dotSize / 2, dotSize, dotSize );
        myGameArea.context.fillRect( x + 3 * dieSize / 4 - dotSize / 2, y + dieSize / 2 - dotSize / 2, dotSize, dotSize );
    }
    myGameArea.context.stroke();
}

function markNation( nation, color ) {
    myGameArea.context.lineWidth=10;
    myGameArea.context.globalAlpha = .50;
    myGameArea.context.strokeStyle = color;
    myGameArea.context.beginPath();
    myGameArea.context.arc( nation.x + mouseOffsetX, nation.y + mouseOffsetY, clickRadius, 0, 2 * Math.PI );
    myGameArea.context.stroke();
    myGameArea.context.globalAlpha = 1;
}

function infoAdvance(to, from) {
    if ( to == null && from == null ) {
        document.getElementById("info-area").innerHTML = "";
    }
    else {
        document.getElementById("info-area").innerHTML = "Click on " + to.name + " to advance troops, on " + from.name + " to stop.";
    }
}
