%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%initial states%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% #program initial.
% #external _heuristic.
package(1..np).

1 { holds(armed(P),0) : package(P) } 1.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%problem description%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% #program problem.

step(0..length).
max(length).
stepless(0..L-1) :- max(L).


%%%%%%%  fluents   %%%%%%%%%

fluent(armed(P))   :- package(P).
inertial(armed(P)) :- package(P).

fluent(dunked(P))   :- package(P).
inertial(dunked(P)) :- package(P).

fluent(clogged).
inertial(clogged).

fluent(unsafe).

%%%%%%%  actions   %%%%%%%%
action(dunk(P)) :- package(P).
action(flush).

%%%%%%  executable  %%%%%%%
executable(dunk(P), T) :- action(dunk(P)), -holds(clogged,T), step(T), not holds(dunked(P),T).

executable(flush,T) :- action(flush), step(T).

%%%%%  direct effects   %%%%%%%
-holds(armed(P),  T+1) :- occurs(dunk(P), T), step(T).
 holds(dunked(P), T+1) :- occurs(dunk(P), T), step(T).

-holds(clogged, T+1)   :- occurs(flush,   T), step(T).

%%%%%  indirect effects   %%%%%%%
 holds(unsafe, T) :- holds(armed(P),   T), step(T).
-holds(unsafe, T) :- not holds(unsafe, T), step(T).


%%%%% occurs  %%%%%%%
occurs(A,S) :- action(A), stepless(S), not &k{ ~ occurs(A,S) }.
bot :- occurs(A,S), not executable(A,S).
:- occurs(A1,S), occurs(A2,S), A1 < A2, stepless(S).

%%%%% goal  %%%%%%%
goal :- -holds(unsafe, LEN), not bot, max(LEN).

:- not &k{ goal }.
