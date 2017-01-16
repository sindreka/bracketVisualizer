var myBackground;
var nations = [];
var attacker;
var reinforcer;

var player = {
    color : "red",
    troopsDue : 3,
    stage : 1
}

function startGame() {
    myBackground = new map(640,400,"maps/first.png");

    nations[0] = new nation(3,"red",[1,2],78,99);
    nations[1] = new nation(3,"blue",[0,2,3],212,221);
    nations[2] = new nation(3,"green",[0,1,3],424,160);
    nations[3] = new nation(3,"orange",[1,2],368,313);


    myGameArea.start();

}

function nation(troops,owner,borders,x,y) {
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
        }
    }
}

var myGameArea = {
    canvas : document.createElement("canvas"),
    start : function() {
        this.canvas.width = 640;
        this.canvas.height = 400;
        this.context = this.canvas.getContext("2d");
        document.body.insertBefore(this.canvas, document.body.childNodes[0]);
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
    myBackground.update();

    for (i = 0; i < nations.length ; i++) { 
        drawText(nations[i].troops,nations[i].owner,nations[i].x,nations[i].y);
    }

    if ( player.stage == 1 && player.troopsDue == 0 ) { player.stage = 2 }

    if ( clicked = click() ) {
        if ( player.stage == 1 && clicked.owner == player.color ) {
            clicked.troops ++;
            player.troopsDue --;
        }

        else if ( player.stage == 2 ){
            if ( clicked.owner == player.color && clicked.troops > 1 ) {
                console.log("Who is attacking?");
                attacker = clicked;
            }
            else if ( clicked.owner != player.color && attacker ) {
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
            if ( dist( nations[i].x,nations[i].y,myGameArea.x - 15,myGameArea.y ) < 50 ** 2 ) { 
                myGameArea.x = false;
                myGameArea.y = false;
                return nations[i] }
        }
    }
    return false;
}
