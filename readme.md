# Science Olympiad Event Selection Site

## Description:
This is a website with the intention of assigning people to their respective events for my school's Science Olympiad team.

This program works using a weighting system, where the action of assigning a specific person to a specific event is given a weight.
This mostly considers peoples' event preferences over all other data.
The other data is taken into account, mostly for tiebreaks.
The reasoning for this is that generally, we'd expect people who want to do certain events to have experience with those events and/or the science behind them.

Then it uses the AC-3 algorithm.
The soft constraint is maximizing the sum of the weights that occur in the final product (i.e. the weights of each person assigned to the events they are assigned to in the end product)
The hard constraint is making teams where enough students are in each event so that there's a roughly even distribution of people and so every event has the minimum number of necessary attendees.
The binary constraints are that each person cannot be in any events that have conflicting time slots and that each person should not be placed in more events than they wish to be in.

There are other minutiae to consider, like the fact that to cap runtime while continuing to search may find better solutions, I stop the program after it finds the first valid solution since the marginal utility of continuing to search is minimal.
It takes into account that the needs for a varsity team are to fill each event at a bare minimum, while the needs for a junior varsity team are to fill each event relatively evenly.
It also considers that some events need more people to be filled and that some events do not have overlapping times (such as build events).

Most importantly, to preserve peoples' top choices, the program only considers data up to a certain few of their top choices, where each person could be put into the number of events they want to be put in, without conflicting time slots.
It also ensures that each event has at least two or three people in its domain, depending on how many people should compete in the event for one team.
If an event is very unpopular, so much so that there are only two or three people who could be put in an event's domain, then instead these people are automatically put in these events' domains so that the program can consider fewer top choices, and get a better overall result.

Currently, the GUI is rather barebones, because I have not had the time to make it look pretty. It is functional, however, which is the important thing.
I have plans to revise the GUI this winter.

Side note: Some functions are deprecated, as they may have been used for debugging or before the program moved from a terminal-run program to a website-run program.
Also, note that while ranking someone's top 17 events is laborious, it does ensure that by the pigeonhole principle, everyone will be able to be placed into 5 events, if that is what the coaches specify for that year.
Any other important specifications can be found in the comments of the Python code itself.

## How to Install and Run:
In VSCode, you can use the Live Server extension to run the program locally.
If you want to use it on a server, you will have to upload the code to a server, but running the HTML file should work from there.

## How to Use:
All instructions regarding usage pop up once the program is run.

## Credits:
Tobjorn Nelson
