var myBackground;
var nations = [];
var attacker;
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
        if ( this.troopsDue > 0 ) {
            clicked = click();
            if ( clicked && clicked.owner == this.color ) {
                clicked.troops++;
                this.troopsDue--;
            }
        }
        else {
            this.stage = 2;
        }
    }
}

function startGame() {
    myBackground = new map(640,400,"maps/first.png");

    nations[0] = new nation(0,3,"red",[1,2],78,99);
    nations[1] = new nation(1,3,"blue",[0,2,3],212,221);
    nations[2] = new nation(2,3,"red",[0,1,3],424,160);
    nations[3] = new nation(3,3,"orange",[1,2],368,313);


    myGameArea.start();

}

function nation(id,troops,owner,borders,x,y) {
    this.id = id;
    this.troops = troops;
    this.owner = owner;
    this.borders = borders;
    this.x = x;
    this.y = y;
    this.attack = function(victim) {
        numAttackers = Math.min(3,this.troops-1);
        numDefenders = Math.min(2,victim.troops);
        atk = dieRoll(numAttackers);
        def = dieRoll(numDefenders);
        drawDice( atk, def, victim.color );
        if (atk[0] > def[0]) { victim.troops--; }
        else { this.troops--; }
        if (numAttackers > 1 && numDefenders > 1) {
            if (atk[1] > def[1]) { victim.troops--; }
            else { this.troops--; }
        }
        if (victim.troops == 0){
            victim.owner = this.owner;
            victim.troops = this.troops - 1;
            this.troops = 1;
        }
    }
}

var myGameArea = {
    canvas : document.createElement("canvas"),
    start : function() {
        this.canvas.width = 640;
        this.canvas.height = 600;
        this.context = this.canvas.getContext("2d");
        document.body.insertBefore(this.canvas, document.body.childNodes[0]);
        this.interval = setInterval(updateGameArea, 1);
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
    myBackground.update();

    if ( player.stage == 1 ) { player.placeTroops(); }

    if ( attacker ) {
        ctx.beginPath();
        ctx.lineWidth=10;
        ctx.globalAlpha = .50;
        ctx.strokeStyle = player.color;
        ctx.fillStyle = player.color;
        ctx.arc( attacker.x + mouseOffsetX, attacker.y + mouseOffsetY, clickRadius, 0, 2 * Math.PI );
        ctx.stroke();
        ctx.globalAlpha = 1;
    }

    if ( atk && def ) {
        drawDice( atk, def, "blue" );
    }

    for (i = 0; i < nations.length ; i++) {
        drawText(nations[i].troops,nations[i].owner,nations[i].x,nations[i].y);
    }


    if ( clicked = click() ) {

        if ( player.stage == 2 ){
            if ( clicked.owner == player.color && clicked.troops > 1 ) {
                console.log("Who is attacking?");
                attacker = clicked;
                atk = null;
                def = null;
            }
            else if ( clicked.owner != player.color && attacker && ~attacker.borders.indexOf(clicked.id) ) {
                console.log("Attack!");
                attacker.attack(clicked);
                if ( attacker.troops < 2 ) {
                    attacker = null;
                }
            }
        }
    }
}

function map(width,height,file) {
    this.image = new Image();
    this.image.src = file;
    this.width = width;
    this.height = height;
    this.update = function() {
        ctx = myGameArea.context;
        ctx.drawImage(this.image,
                0, 0,
                this.width, this.height);
    }
}

function drawText(text, color, x, y) {
    ctx = myGameArea.context;
    ctx.font = "30px monospace";
    ctx.fillStyle = color;
    ctx.fillText(text, x, y);
}

function dieRoll(num) {
    results = [];
    for (i = 0 ; i < num ; i++) {
        results[i] = Math.ceil(Math.random() * 6);
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

function drawDice( atk, def, victim ) {
    var x = 10;
    var y = myBackground.height + 5;
    var dieSize = 30;
    for (i = 0 ; i < atk.length ; i++ ) {
        if ( def[i] && atk[i] > def[i] ) {
            ctx.fillStyle = "#666699";
            ctx.fillRect( x-3, y-3, dieSize + 6, dieSize + 6 );
            //ctx.stroke();
        }
        drawDie( atk[i], x, y, dieSize, player.color );
        x += dieSize + 10;
    }
    x += 15;
    for (i = 0 ; i < def.length ; i++ ) {
        if ( atk[i] && def[i] >= atk[i] ) {
            ctx.fillStyle = "#666699";
            ctx.fillRect( x-3, y-3, dieSize + 6, dieSize + 6 );
        }
        drawDie( def[i], x, y, dieSize, victim );
        x += dieSize + 10;
    }
}

function drawDie( num, x, y, dieSize, color ) {
    var dotSize = 2;
    ctx.fillStyle = color;
    ctx.lineWidth = 2;
    ctx.fillRect(x, y, dieSize, dieSize);
    ctx.stroke();
    ctx.strokeStyle = "white";
    if ( num == 1 || num == 3 || num == 5 ) {
        ctx.rect( x + dieSize / 2 - dotSize / 2, y + dieSize / 2 - dotSize / 2, dotSize, dotSize );
    }
    if ( num == 2 || num == 3 ) {
        ctx.rect( x + dieSize / 3 - dotSize / 2, y + dieSize / 3 - dotSize / 2, dotSize, dotSize );
        ctx.rect( x + 2 * dieSize / 3 - dotSize / 2, y + 2 * dieSize / 3 - dotSize / 2, dotSize, dotSize );
    }
    if ( num == 4 || num == 5 || num == 6 ) {
        ctx.rect( x + dieSize / 3 - dotSize / 2, y + dieSize / 3 - dotSize / 2, dotSize, dotSize );
        ctx.rect( x + dieSize / 3 - dotSize / 2, y + 2 * dieSize / 3 - dotSize / 2, dotSize, dotSize );
        ctx.rect( x + 2 * dieSize / 3 - dotSize / 2, y + dieSize / 3 - dotSize / 2, dotSize, dotSize );
        ctx.rect( x + 2 * dieSize / 3 - dotSize / 2, y + 2 * dieSize / 3 - dotSize / 2, dotSize, dotSize );
    }
    if ( num == 6 ) {
        ctx.rect( x + dieSize / 3 - dotSize / 2, y + dieSize / 2 - dotSize / 2, dotSize, dotSize );
        ctx.rect( x + 2 * dieSize / 3 - dotSize / 2, y + dieSize / 2 - dotSize / 2, dotSize, dotSize );
    }
    ctx.stroke();
}
