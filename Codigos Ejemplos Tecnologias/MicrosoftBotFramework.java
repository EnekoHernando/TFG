const { ActivityHandler } = require('botbuilder');
class MyBot extends ActivityHandler {
    constructor() {
        super();
        this.onMessage(async (context, next) => {
            await context.sendActivity(`You said '${ context.activity.text }'`);
            await next();
        });
    }
}
