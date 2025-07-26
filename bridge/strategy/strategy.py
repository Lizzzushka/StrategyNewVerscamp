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

    def run(self, field: fld.Field, actions: list[Optional[Action]]) -> None:
        """
        ONE ITERATION of strategy
        NOTE: robots will not start acting until this function returns an array of actions,
              if an action is overwritten during the process, only the last one will be executed)

        Examples of getting coordinates:
        - field.allies[8].get_pos(): aux.Point -   coordinates  of the 8th  robot from the allies
        - field.enemies[14].get_angle(): float - rotation angle of the 14th robot from the opponents

        - field.ally_goal.center: Point - center of the ally goal
        - field.enemy_goal.hull: list[Point] - polygon around the enemy goal area


        Examples of robot control:
        - actions[2] = Actions.GoToPoint(aux.Point(1000, 500), math.pi / 2)
                The robot number 2 will go to the point (1000, 500), looking in the direction π/2 (up, along the OY axis)

        - actions[3] = Actions.Kick(field.enemy_goal.center)
                The robot number 3 will hit the ball to 'field.enemy_goal.center' (to the center of the enemy goal)

        - actions[9] = Actions.BallGrab(0.0)
                The robot number 9 grabs the ball at an angle of 0.0 (it looks to the right, along the OX axis)
        """
        """angell =  (field.ball.get_pos() - field.allies[self.idx].get_pos()).arg()
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
            print(mediana) """    

        angell =  (field.ball.get_pos() - field.allies[self.idx].get_pos()).arg()
        vecBallRob = aux.point_on_line(field.ball.get_pos(), field.enemies[0].get_pos(), -500)    
        actions[self.idx] = Actions.GoToPointIgnore(vecBallRob, angell)     