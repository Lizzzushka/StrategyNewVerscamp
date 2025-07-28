"""High-level strategy code"""

# !v DEBUG ONLY
import math  # type: ignore
from time import time  # type: ignore
from typing import Optional

from bridge import const
from bridge.auxiliary import aux, fld, rbt  # type: ignore
from bridge.const import State as GameStates
from bridge.router.base_actions import Action, Actions, KickActions  # type: ignore


class Strategy:
    """Main class of strategy"""

    def __init__(
        self,
    ) -> None:
        self.we_active = False
        self.idx = 2
        self.puinum = 1


    def process(self, field: fld.Field) -> list[Optional[Action]]:
        """Game State Management"""
        if field.game_state not in [GameStates.KICKOFF, GameStates.PENALTY]:
            if field.active_team in [const.Color.ALL, field.ally_color]:
                self.we_active = True
            else:
                self.we_active = False

        actions: list[Optional[Action]] = []
        for _ in range(const.TEAM_ROBOTS_MAX_COUNT):
            actions.append(None)

        if field.ally_color == const.COLOR:
            text = str(field.game_state) + "  we_active:" + str(self.we_active)
            field.strategy_image.print(aux.Point(600, 780), text, need_to_scale=False)
        match field.game_state:
            case GameStates.RUN:
                self.run(field, actions)
            case GameStates.TIMEOUT:
                pass
            case GameStates.HALT:
                return [None] * const.TEAM_ROBOTS_MAX_COUNT
            case GameStates.PREPARE_PENALTY:
                pass
            case GameStates.PENALTY:
                pass
            case GameStates.PREPARE_KICKOFF:
                pass
            case GameStates.KICKOFF:
                pass
            case GameStates.FREE_KICK:
                pass
            case GameStates.STOP:
                # The router will automatically prevent robots from getting too close to the ball
                self.run(field, actions)

        return actions

    def choose_on_goal(field: fld.Field, actions: list[Action]) -> None:
        anglelU = abs(aux.get_angle_between_points(field.enemies[const.ENEMY_GK].get_pos(), field.allies[self.idx].get_pos(), field.enemy_goal.down))
        anglelD = abs(aux.get_angle_between_points(field.enemies[const.ENEMY_GK].get_pos(), field.allies[self.idx].get_pos(), field.enemy_goal.up))
        if anglelD > anglelU:
            go = field.enemy_goal.down + (field.enemy_goal.eye_up * 110)
        else:
             go = field.enemy_goal.down + (field.enemy_goal.eye_up * -110)   
        actions[self.idx] = Actions.Kick(go)    
        


    def run(self, field: fld.Field, actions: list[Optional[Action]]) -> None:

        angell =  (field.ball.get_pos() - field.allies[self.idx].get_pos()).arg()
        if field.ally_color == const.Color.YELLOW:
            self.choose_on_goal(field, actions)
        else:
             vecBallRob2 = aux.get_line_intersection(field.ball.get_pos(), field.enemies[self.idx].get_pos(), field.ally_goal.center_up, "RS")   

        if vecBallRob2 is None:
            vecBallRob2 = field.ally_goal.center_up()
        actions[const.GK] = Actions[vecBallRob2, angell]
        vecBallRob = aux.point_on_line(field.ball.get_pos(), field.enemies[0].get_pos(), -500)    
        actions[self.idx] = Actions.GoToPointIgnore(vecBallRob, angell)  
        print(field.allies[self.idx].get_pos())
     
       
        angell =  (field.ball.get_pos() - field.allies[self.idx].get_pos()).arg()
        if self.puinum == 1:
            actions[self.idx] = Actions.GoToPointIgnore(field.ball.get_pos(), angell)

        disttball = aux.dist(field.ball.get_pos(), field.active_allies[self.idx].get_pos())
        if disttball < 200:
            self.puinum = 2
        elif self.puinum == 2:
            myGoalPoint = field.ally_goal
            GoalPoint = field.ally_goal
            mgp = aux.nearest_point_on_poly(field.allies[self.idx].get.pos(), myGoalPoint)
            gp = aux.nearest_point_on_poly(field.allies[self.idx].get.pos(), GoalPoint)
        if aux.dist(field.allies[self.idx].get_pos(), mgp) < aux.dist(field.allies[self.idx].get_pos(), gp):
            mgp = gp
        actions[self.idx] = Actions.GoToPointIgnore(mgp, angell)
        distgoal = aux.dist(gp, field.allies[self.idx].get_pos())
        if distgoal < 200:
            self.puinum = 1
        angleBlue = field.enemies[0].get_angle()   
        angleYel = field.allies[0].get_angle()
        angleYel4 = field.allies[4].get_angle()   
        
        vecBT = aux.Point(500, 0)
        vecYT = aux.Point(500, 0)
        vecYTT = aux.Point(500, 0)  
        
        vecY0 = aux.rotate(vecYT, angleYel)
        vecB0 = aux.rotate(vecBT, angleBlue) 
        vecY4 = aux.rotate(vecYTT, angleYel4) 

        pointintr1 = aux.get_line_intersection(vecB0.unity() + field.enemies[0].get_pos(), vecB0.unity() * 2 + field.enemies[0].get.pos(), vecY0.unity() + field.allies[0].get.pos(), vecY0.unity() * 2 + field.allies[0].get_pos(), "LL" )
        pointintr2 = aux.get_line_intersection(vecB0.unity() + field.enemies[0].get_pos(), vecY4.unity() * 2 + field.enemies[0].get.pos(), vecY4.unity()  + field.allies[4].get.pos(), vecY4.unity() * 2 + field.allies[4].get_pos(), "LL" )
        pointintr3 = aux.get_line_intersection(vecY4.unity() + field.allies[4].get_pos(), vecY0.unity() * 2 + field.allies[4].get.pos(), vecY0.unity()  + field.allies[0].get.pos(), vecY0.unity() * 2 + field.allies[0].get_pos(), "LL" )
    
        if pointintr1 is None or pointintr2 is None or pointintr3 is None:
            print("Нет пересечений")
        else:
            mediana = (pointintr1 + pointintr2 + pointintr3) / 3
            print(mediana) 