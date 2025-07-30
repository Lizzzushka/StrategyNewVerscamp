"""High-level strategy code"""

# !v DEBUG ONLY
from time import time

from bridge import const
from bridge.auxiliary import aux, fld, rbt
from bridge.const import State as GameStates
from bridge.router.base_actions import Action, Actions, KickActions
from typing import Optional
import math


ball_in_robot = None
ball_in_robot_enem = None
ball_start = None

voltage_kik = 15
voltage_pas = 4

class Strategy:
    """Main class of strategy"""

    def __init__(
            self,
    ) -> None:
        self.we_active = False

        self.target_point = aux.Point(100, 100)
        self.current = 0
        self.robot_with_ball: Optional[rbt.Robot] = None

        # Индексы роботов
        self.gk_idx = 1
        self.idx1 = 2   
        self.idx2 = 4  
        
        # Индексы роботов соперника
        self.gk_idx_enem = 3
        self.idx_enem1 = 5
        self.idx_enem2 = 6

        
    def process(self, field: fld.Field) -> list[Action]:
        #print(GameStates)
        """Game State Management"""
        if field.game_state not in [GameStates.KICKOFF, GameStates.PENALTY]:
            if field.active_team in [const.Color.ALL, field.ally_color]:
                self.we_active = True
            else:
                self.we_active = False

        actions: list[Action] = []
        for _ in range(const.TEAM_ROBOTS_MAX_COUNT):
            actions.append(Actions.Stop())
        #actions[1] = Actions.GoToPoint(aux.Point(2000,0),0)
        if field.ally_color == const.COLOR:
            text = str(field.game_state) + "  we_active:" + str(self.we_active)
            field.strategy_image.print(aux.Point(600, 780), text, need_to_scale=False)

        if self.we_active == const.Color.ALL:
            self.we_active = True
        if const.COLOR == const.Color.BLUE:
            self.we_active = field.active_team == const.Color.BLUE
        else:
            self.we_active = field.active_team == const.Color.YELLOW

        if field.game_state not in [GameStates.KICKOFF, GameStates.PENALTY]:
            if field.active_team in [const.Color.ALL, field.ally_color]:
                self.we_active = True
            else:
                self.we_active = False
        ##########################coordinates_our##########################
        robot_pos_gk = field.allies[self.gk_idx].get_pos()
        robot_pos1 = field.allies[self.idx1].get_pos()
        robot_pos2 = field.allies[self.idx2].get_pos()

        ##########################coordinates_ali##########################
        robot_pos_gk_enem = field.enemies[self.gk_idx_enem].get_pos()
        robot_pos1_enem = field.enemies[self.idx_enem1].get_pos()
        robot_pos2_enem = field.enemies[self.idx_enem2].get_pos()

        ball = field.ball.get_pos()

        print(self.we_active)
        print(field.game_state)

        if field.game_state == GameStates.RUN:
            self.run(field, actions)
            
        elif field.game_state == GameStates.TIMEOUT:
            pass
        elif field.game_state == GameStates.HALT:
            actions[self.idx1] = Actions.Stop()
            actions[self.idx2] = Actions.Stop()
            return actions
           
        elif field.game_state == GameStates.PREPARE_PENALTY:
            kik_angle1 = robot_pos1_enem - robot_pos1
            kik_angle2 = robot_pos2_enem - robot_pos2
            pos_kikoff1 = aux.Point(500, 0)
            pos_kikoff2 = aux.Point(1000, 0)
            actions[self.idx1] = Actions.GoToPoint(pos_kikoff1, kik_angle1.arg())
            actions[self.idx2] = Actions.GoToPoint(pos_kikoff2, kik_angle2.arg())
            return actions
        
        elif field.game_state == GameStates.PENALTY and not self.we_active:
            position_penalty1 = ball
            angle_penalty1 = ball - robot_pos1
            actions[self.idx1] = Actions.GoToPoint(position_penalty1, angle_penalty1.arg())

            return actions

        elif field.game_state == GameStates.PENALTY and self.we_active:
            g_up_xy_attacker = field.enemy_goal.up - field.enemy_goal.eye_up * 90   #определяется угол ворот противоположный от враторя
            g_down_xy_attacker = field.enemy_goal.down + field.enemy_goal.eye_up * 90

            up_attacker = (g_up_xy_attacker - robot_pos_gk_enem).mag()
            down_attacker = (robot_pos_gk_enem - g_down_xy_attacker).mag()



            if up_attacker > down_attacker:
                position_attacker_gate = g_up_xy_attacker
            else:
                position_attacker_gate = g_down_xy_attacker
        
            actions[self.idx1] = Actions.Kick(position_attacker_gate, voltage_kik)

            return actions

        elif field.game_state == GameStates.PREPARE_KICKOFF:
            kik_angle1 = robot_pos1_enem - robot_pos1
            kik_angle2 = robot_pos2_enem - robot_pos2
            pos_kikoff1 = aux.Point(-500, 0)   #+
            pos_kikoff2 = aux.Point(-1000, 0)
            actions[self.idx1] = Actions.GoToPoint(pos_kikoff1, kik_angle1.arg())
            actions[self.idx2] = Actions.GoToPoint(pos_kikoff2, kik_angle2.arg())
            
            return actions
    
            
        elif field.game_state == GameStates.KICKOFF and  not self.we_active:
            kik_angle1 = robot_pos1_enem - robot_pos1
            kik_angle2 = robot_pos2_enem - robot_pos2
            pos_kikoff1 = aux.Point(500, 0)
            pos_kikoff2 = aux.Point(000, 0)
            actions[self.idx1] = Actions.GoToPoint(pos_kikoff1, kik_angle1.arg())
            actions[self.idx2] = Actions.GoToPoint(pos_kikoff2, kik_angle2.arg())
            return actions

        elif field.game_state == GameStates.KICKOFF and self.we_active:
            self.run(field, actions)
            return actions

        elif field.game_state == GameStates.FREE_KICK:
            self.run(field, actions)
            pass

        elif field.game_state == GameStates.STOP:
            ball_pos = field.ball.get_pos()
                        
            robot_to_ball1 = ball_pos - robot_pos1
            robot_to_ball2 = ball_pos - robot_pos2
                        
            if robot_to_ball1.mag() > 50:
                deltac = 50 - robot_to_ball1.x
                pos_stop1 = aux.Point(ball.x + deltac, robot_to_ball1.y)
                actions[self.idx1] = Actions.GoToPoint(pos_stop1, robot_to_ball1.arg())
            else:
                
                actions[self.idx1] = Actions.GoToPoint(robot_to_ball1, robot_to_ball1.arg())
            if robot_to_ball2.mag() > 50:
                deltac = 50 - robot_to_ball2.x
                pos_stop2 = aux.Point(ball.x + deltac, robot_to_ball2.y)
                
                actions[self.idx2] = Actions.GoToPoint(pos_stop2, robot_to_ball2.arg())
            else:
                actions[self.idx2] = Actions.GoToPoint(robot_to_ball2, robot_to_ball2.arg())
            return actions
        
        return actions
    
    def is_ball_moves_to_point(self, robot_pos1: aux.Point, ball) -> bool:
        """Определить, движется ли мяч в сторону точки"""
        vec_to_point = robot_pos1 - ball.get_pos()
        return (
            ball.get_vel().mag() * (math.cos(vec_to_point.arg() - ball.get_vel().arg()) ** 5)
            > const.INTERCEPT_SPEED * 5
            and self.robot_with_ball is None
            and abs(vec_to_point.arg() - ball.get_vel().arg()) < math.pi / 2
        )

    def is_opponent_near_ball(self, field: fld.Field, distance: float = 0) -> bool:
        ball_pos = field.ball.get_pos()
        for enemy in field.enemies:
            enemy_pos = enemy.get_pos()
            if (enemy_pos - ball_pos).mag() < distance:
                return True
        return False
        

    def run(self, field: fld.Field, actions: list[Action]) -> None:
        """
        Assigning roles to robots and managing them
            roles - robot roles sorted by priority
            robot_roles - list of robot id and role matches
        """
        print("zzz")
        self.attacker(field, actions, self.idx1)
        self.goalkeeper(field, actions, )

    def attacker(self, field: fld.Field, actions: list[Action], idx: int) -> None:
        ball = field.ball.get_pos()
        dist_ball1 = (ball - field.allies[self.idx1].get_pos()).mag()#fieels.allies
        
        dist_ball2 = (ball - field.allies[self.idx2].get_pos()).mag()

        ##########################coordinates_our##########################
        robot_pos_gk = field.allies[self.gk_idx].get_pos()
        robot_pos1 = field.allies[self.idx1].get_pos()
        robot_pos2 = field.allies[self.idx2].get_pos()

        ##########################coordinates_ali##########################
        robot_pos_gk_enem = field.enemies[self.gk_idx_enem].get_pos()
        robot_pos1_enem = field.enemies[self.idx_enem1].get_pos()
        robot_pos2_enem = field.enemies[self.idx_enem2].get_pos()

        ##########################ball##########################
        ball = field.ball.get_pos()

        pas = 0 

                    
        ##########################attacker##########################
        g_up_xy_attacker = field.enemy_goal.up - field.enemy_goal.eye_up * 40   #определяется угол ворот противоположный от враторя
        g_down_xy_attacker = field.enemy_goal.down + field.enemy_goal.eye_up * 40

        up_attacker = (g_up_xy_attacker - robot_pos_gk_enem).mag()
        down_attacker = (robot_pos_gk_enem - g_down_xy_attacker).mag()


        distance1 = (robot_pos_gk - robot_pos1_enem).mag()
        distamce2 = (robot_pos_gk - robot_pos2_enem).mag()

        dist_ball_robot1 = (ball - robot_pos1_enem).mag()
        dist_ball_robot2 = (ball - robot_pos2_enem).mag()

        if dist_ball_robot1 < dist_ball_robot2:
            dist_ball_enm = robot_pos1_enem
        else:
            dist_ball_enm = robot_pos2_enem


        attacker_position = ball

        if up_attacker > down_attacker:
            position_attacker_gate = g_up_xy_attacker
        else:
            position_attacker_gate = g_down_xy_attacker     #закончилось

        if distance1 < distamce2:            #смотрится кто дальше находится от враторя  
            if robot_pos2_enem.x > robot_pos1.x:         #находится ли робот относительно мяча с право или слева    
                field.strategy_image.draw_line(robot_pos1, position_attacker_gate, (255, 0, 0), 5)

                actions[self.idx1] = Actions.Kick(position_attacker_gate, voltage_kik)


            else:
                #бъёт между роботов в противоположный угол
                vector_robot = ((robot_pos_gk_enem - robot_pos2_enem) / 2) + robot_pos1 # blu -
                angle_atacker = position_attacker_gate - vector_robot
                field.strategy_image.draw_line(robot_pos2_enem, robot_pos_gk_enem, (0, 0, 255), 5)
                field.strategy_image.draw_line(robot_pos1, position_attacker_gate, (255, 0, 0), 5)

                actions[self.idx1] = Actions.Kick(angle_atacker, voltage_kik)

                

        else:
            if robot_pos1_enem.y > robot_pos1.y:     #находится ли робот относительно мяча с право или слева
                field.strategy_image.draw_line(robot_pos1, position_attacker_gate, (255, 0, 0), 5)

                actions[self.idx1] = Actions.Kick(position_attacker_gate, voltage_kik)


            else:
                #бъёт между роботов в противоположный угол
                vector_robot = ((robot_pos_gk_enem - robot_pos1_enem) / 2) + robot_pos1 # blu -
                angle_atacker = position_attacker_gate - vector_robot
                field.strategy_image.draw_line(robot_pos1_enem, robot_pos_gk_enem, (0, 0, 255), 5)
                field.strategy_image.draw_line(robot_pos1, position_attacker_gate, (255, 0, 0), 5)

                actions[self.idx1] = Actions.Kick(angle_atacker, voltage_kik)


        if self.is_opponent_near_ball(field):
            pas = 1
            field.strategy_image.draw_line(robot_pos1, robot_pos2, (0,255,0), 5)
            actions[self.idx1] = Actions.Kick(robot_pos2, voltage_kik)


        ###################protection###################

        # Определяем, какой робот ближе к мячу
        ###################защита#################
        ball_in_robot_enem = None
        angle_protection = ball
        protection_position = ball


        g_up_xy_protection = field.ally_goal.up - field.ally_goal.eye_forw * 70    #определяется угол ворот противоположный от враторя
        g_down_xy_protection = field.ally_goal.down + field.ally_goal.eye_forw * 70

        up_protection = (g_up_xy_protection - robot_pos_gk).mag()
        down_protection = (robot_pos_gk - g_down_xy_protection).mag()

        if up_protection < down_protection:
            protection_position_gate = g_up_xy_protection
        else:
            protection_position_gate = g_down_xy_protection

        #field.allies[self.idx2].set_dribbler_speed(1)

        #print(field.is_ball_in(field.allies[self.idx2]))

        if field.is_ball_in(field.allies[self.idx2]):
            field.strategy_image.draw_line(robot_pos2, angle_protection, (255, 0, 0), 5)
            angle_protection = position_attacker_gate - robot_pos2

            angle_atacker = robot_pos2 - robot_pos1

            protection_position = ball
            attacker_position = aux.Point(dist_ball_enm.x - 300, dist_ball_enm.y)

            actions[self.idx1] = Actions.GoToPoint(attacker_position, angle_atacker.arg())
            actions[self.idx2] = Actions.Kick(robot_pos2, voltage_kik)
            return actions

        if pas == 1:
            field.allies[self.idx2].set_dribbler_speed(1)
            if robot_pos1.y > 0:
                protection_position = aux.Point(robot_pos1.x + 500, robot_pos1.y - 500)
                angle_protection = (robot_pos1 - robot_pos2)
                angle_atacker = (robot_pos2 - robot_pos1)
                actions[self.idx1] = Actions.Kick(robot_pos2, voltage_pas)
                actions[self.idx2] = Actions.GoToPoint(protection_position, angle_protection.arg())
            else:
                protection_position = aux.Point(dist_ball_enm.x + 300, dist_ball_enm.y - 500)
                angle_protection = (robot_pos1 - robot_pos2)
                actions[self.idx1] = Actions.Kick(robot_pos2, voltage_pas)
                actions[self.idx2] = Actions.GoToPoint(protection_position, angle_protection.arg())
        else:
            if dist_ball_enm.x < 0:
                protection_position = aux.Point(dist_ball_enm.x + 300, dist_ball_enm.y) # Blu -
                angle_protection = (dist_ball_enm - robot_pos2)
                actions[self.idx2] = Actions.GoToPoint(protection_position, angle_protection.arg())
            else:
                protection_position = aux.closest_point_on_line(protection_position_gate, dist_ball_enm, robot_pos2)
                angle_protection = (dist_ball_enm - robot_pos2)
                actions[self.idx2] = Actions.GoToPoint(protection_position, angle_protection.arg())
        
        if field.is_ball_in(field.enemies[self.idx1]) or field.is_ball_in(field.enemies[self.idx2]):
            oblique_robot1 = aux.get_tangent_points(robot_pos1, ball, const.ROBOT_R)
            oblique_robot2 = aux.get_tangent_points(robot_pos2, ball, const.ROBOT_R)

            if len(oblique_robot1) >= 2 and len(oblique_robot2) >= 2:

                field.strategy_image.draw_line(oblique_robot1[0], dist_ball_enm, (255, 0, 0), 5)
                field.strategy_image.draw_line(oblique_robot1[1], dist_ball_enm, (255, 0, 0), 5)

                field.strategy_image.draw_dot(oblique_robot1[0], (255, 0, 0), 50)
                field.strategy_image.draw_dot(oblique_robot1[1], (255, 0, 0), 50)

                field.strategy_image.draw_line(oblique_robot2[0], dist_ball_enm, (255, 0, 0), 5)
                field.strategy_image.draw_line(oblique_robot2[1], dist_ball_enm, (255, 0, 0), 5)

                field.strategy_image.draw_dot(oblique_robot2[0], (255, 0, 0), 50)
                field.strategy_image.draw_dot(oblique_robot2[1], (255, 0, 0), 50)
                angle_protection = dist_ball_enm

            #if oblique_robot1[0].distance_to(oblique_robot2[0]) < oblique_robot1[0].distance_to(oblique_robot2[1]):
            #    protection_position1 = oblique_robot1[1]
            #    protection_position2 = oblique_robot2[0]

            #else:
            #    protection_position1 = oblique_robot1[0]
            #    protection_position2 = oblique_robot2[1]

            #protection_position_oblique1 = aux.closest_point_on_line(protection_position_gate, robot_pos2_enem, protection_position1)
            #protection_position_oblique2 = aux.closest_point_on_line(protection_position_gate, robot_pos2_enem, protection_position2)

            #attacker_position = aux.Point(protection_position1.x - 100, protection_position_oblique1.y )
            #protection_position = aux.Point(protection_position2.x - 100, protection_position_oblique2.y )

            #angle_atacker = (robot_pos2_enem - protection_position1)
            #angle_protection = (robot_pos2_enem - protection_position2)
        print(2, protection_position)
        field.strategy_image.draw_line(dist_ball_enm, protection_position_gate, (0, 0, 255), 5)  

        print(pas)
        return actions


    def goalkeeper(self, field: fld.Field, actions: list[Action]) -> None:
        # Получаем позиции союзных роботов
        robot_pos_gk = field.allies[self.gk_idx].get_pos()
        robot_pos1 = field.allies[self.idx1].get_pos()
        robot_pos2 = field.allies[self.idx2].get_pos()
    
        # Получаем позиции вражеских роботов
        robot_pos_gk_enem = field.enemies[self.gk_idx_enem].get_pos()
        robot_pos1_enem = field.enemies[self.idx_enem1].get_pos()
        robot_pos2_enem = field.enemies[self.idx_enem2].get_pos()
    
        # Получаем позицию мяча
        ball = field.ball.get_pos()


        g_up_xy_goal = field.enemy_goal.up - field.enemy_goal.eye_up * 70    
        g_down_xy_goal = field.enemy_goal.down + field.enemy_goal.eye_up * 70

        up_goal = (g_up_xy_goal - robot_pos_gk_enem).mag()
        down_goal = (robot_pos_gk_enem + g_down_xy_goal).mag()

        if up_goal > down_goal:
            goal_position_gates = g_up_xy_goal
        else:
            goal_position_gates = g_down_xy_goal     

        angle_goal_ball = (goal_position_gates - robot_pos_gk).arg()

    
        if field.ball_start_point is not None:
            goal_position = aux.closest_point_on_line(field.ball_start_point, ball, robot_pos_gk, "R")
        else:
            goal_position = field.ally_goal.center

        position_goal = aux.is_point_inside_poly(goal_position, field.ally_goal.hull)

        if position_goal == False:
            goal_position = field.ally_goal.center

        angle_goalkeeper = (ball - robot_pos_gk).arg()
    
        actions[self.gk_idx] = Actions.GoToPoint(goal_position, angle_goal_ball)

    
        if field.is_ball_stop_near_goal():
            actions[self.gk_idx] = Actions.Kick(goal_position_gates, voltage_kik, is_upper=True)

    
        if field.is_ball_in(field.allies[self.gk_idx]):
            actions[self.gk_idx] = Actions.Kick(goal_position_gates, voltage_kik,is_upper=True)
                
        return actions