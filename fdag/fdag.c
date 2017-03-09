#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <pthread.h>

#define V 50

double C1 = 2.0;
double C2 = 1.0;
double C3 = 1.0;
double C4 = 0.1;

bool THREADED = false;
unsigned NUM_THREADS = 4;

struct vec2 {
	double x;
	double y;
};

struct edge {
	int v;
	int w;
};

double
distance(struct vec2 *from, struct vec2 *to)
{
	return sqrt( pow(from->x - to->x, 2) + pow(from->y - to->y, 2) );
}

double
repulsion(double distance)
{
	double denom = distance > C2 ? distance : C2;
	return (C3 / pow(denom, 2));
}

double
attraction(double distance)
{
	return C1 * log10(distance / C2);
}

struct vec2
unit_vec(struct vec2 *from, struct vec2 *to)
{
	struct vec2 vec;

	double x3 = to->x - from->x;
	double y3 = to->y - from->y;

	double magnitude = sqrt( pow(x3, 2) + pow(y3, 2) );

	if (isnormal(magnitude)) {
		vec.x = x3 / magnitude;
		vec.y = y3 / magnitude;
	}
	else {
		vec.x = 0.0;
		vec.y = 0.0;
	}

	return vec;
}

void
apply_vforce(struct vec2 *p1, struct vec2 *p2)
{
	double d = distance(p1, p2);
	double f = repulsion(d) * C4;
	struct vec2 unit = unit_vec(p2, p1);

	p1->x += unit.x * f;
	p1->y += unit.y * f;
}

void
apply_vertforces(struct vec2 *vertices, int n)
{
	struct vec2 new_vertices[n];

	for (int i = 0; i < n; i++) {

		new_vertices[i] = vertices[i];

		for (int j = 0; j < n; j++) {
			if (j != i) {
				apply_vforce(&new_vertices[i], &vertices[j]);
			}
		}
	}

	for (int i = 0; i < n; i++) {
		vertices[i] = new_vertices[i];
	}
};

struct apply_vforces_args {
	struct vec2 *vertices;
	struct vec2 *new_vertices;
	int begin;
	int end;
	int n;
};

void *
apply_vforces_thread(void *args)
{
	/*
	 * Update vertices[begin] through vertices[end]
	 */

	int result;

	// Unpack args
	struct vec2 *new_vertices = ((struct apply_vforces_args *)args)->new_vertices;
	struct vec2 *vertices = ((struct apply_vforces_args *)args)->vertices;
	int begin = ((struct apply_vforces_args *)args)->begin;
	int end = ((struct apply_vforces_args *)args)->end;
	int n = ((struct apply_vforces_args *)args)->n;

	// Apply vforces
	for (int i = begin; i <= end; i++) {
		for (int j = 0; j < n; j++) {
			if (i != j) { // Don't apply force to yourself
				apply_vforce(&new_vertices[i], &vertices[j]);
			}
		}
	}

	pthread_exit(0);

}

void apply_vertforces_threaded(struct vec2 *vertices, int n)
{
	int result;
	struct vec2 new_vertices[n];
	struct apply_vforces_args args[NUM_THREADS];
	pthread_t threads[NUM_THREADS];

	int chunk_size = n / NUM_THREADS;

	// Copy vertices into new_vertices
	for (int i = 0; i < n; i++) {
		new_vertices[i] = vertices[i];
	}

	for (int i = 0; i < NUM_THREADS; i++) {
		args[i].vertices = vertices;
		args[i].new_vertices = &new_vertices[0];
		args[i].n = n;
		args[i].begin = i * chunk_size;
		args[i].end = (i < (NUM_THREADS - 1)) ? (((i + 1) * chunk_size) - 1) : n - 1;

		result = pthread_create(&(threads[i]), NULL, apply_vforces_thread, (void *)&(args[i]));
		assert (!result);
	}

	for (int i = 0; i < NUM_THREADS; i++) {
		result = pthread_join(threads[i], NULL);
		assert (!result);
	}

	for (int i = 0; i < n; i++) {
		vertices[i] = new_vertices[i];
	}
}

void
apply_edgeforces(struct vec2 *vertices, int num_vertices, struct edge *edges, int num_edges)
{
	struct vec2 vert_delta[num_vertices];
	for (int i = 0; i < num_vertices; i++) {
		vert_delta[i].x = 0.0;
		vert_delta[i].y = 0.0;
	}

	for (int i = 0; i < num_edges; i++) {
		int v = edges[i].v;
		int w = edges[i].w;

		double d = distance(&(vertices[v]), &(vertices[w]));
		double f = attraction(d) * C4;

		if (!isnormal(f)) {
			continue;
		}

		struct vec2 unit = unit_vec(&(vertices[v]), &(vertices[w]));
		struct vec2 delta;

		delta.x = unit.x * f;
		delta.y = unit.y * f;

		if (!isnormal(delta.x) || !isnormal(delta.y)) {
			continue;
		}

		vert_delta[v].x += delta.x;
		vert_delta[v].y += delta.y;

		vert_delta[w].x -= delta.x;
		vert_delta[w].y -= delta.y;
	}

	for (int i = 0; i < num_vertices; i++) {
		vertices[i].x += vert_delta[i].x;
		vertices[i].y += vert_delta[i].y;
	}
}

static PyObject *
fdag(PyObject *self, PyObject *args)
{
	/*
	 * When calling this function from python the arguments should be
	 * 	1) A list of tuples of floats representing x,y coords
	 * 	   of a vertex
	 * 	2) The length of that list
	 * 	3) A list of tuples of ints representing connections between
	 * 	   the vertices of the previous list. The ints being indices
	 * 	   into the list.
	 * 	4) The length of that list
	 *
	 * The function returns a modified list of tuples representing vertices.
	 */

	PyObject *vert_obj;
	PyObject *edge_obj;

	int i, num_verts, num_edges;
	bool verts_done = false;
	bool edges_done = false;

	// Parse the argument tuple. O -> PyObject, i -> int
	if (!PyArg_ParseTuple(args, "OiOi", &vert_obj, &num_verts, &edge_obj, &num_edges)) {
		return NULL;
	}

	// Get iterators from PyObjects
	PyObject *vert_iter = PyObject_GetIter(vert_obj);
	PyObject *edge_iter = PyObject_GetIter(edge_obj);

	if (!vert_iter || !edge_iter) {
		return NULL;
	}

	struct vec2 *vertices = malloc(sizeof(struct vec2) * num_verts);
	struct edge *edges = malloc(sizeof(struct edge) * num_edges);

	i = 0;
	while (!(verts_done && edges_done)) {
		if (!verts_done) {
			// Fill vertices array
			double x, y;

			PyObject *next_vert = PyIter_Next(vert_iter);
			if (!next_vert) {
				return NULL;
			}

			if (!PyArg_ParseTuple(next_vert, "dd", &x, &y)) {
				return NULL;
			}

			assert(i < num_verts);

			vertices[i].x = x;
			vertices[i].y = y;

			Py_DECREF(next_vert);

			if (i == num_verts - 1) {
				verts_done = true;
			}

		}

		if (!edges_done) {
			// Fill edges array
			int v, w;

			PyObject *next_edge = PyIter_Next(edge_iter);
			if (!next_edge) {
				return NULL;
			}

			if (!PyArg_ParseTuple(next_edge, "ii", &v, &w)) {
				return NULL;
			}

			assert(i < num_edges);

			edges[i].v = v;
			edges[i].w = w;

			Py_DECREF(next_edge);

			if (i == num_edges - 1) {
				edges_done = true;
			}
		}

		i++;
	}


	// Should do this on failure as well...
	Py_DECREF(vert_iter);
	Py_DECREF(edge_iter);

	// Do what we came here for
	if (THREADED) {
		apply_vertforces_threaded(vertices, num_verts);
	}
	else {
		apply_vertforces(vertices, num_verts);
	}

	apply_edgeforces(vertices, num_verts, edges, num_edges);

	// Create and populate a python list to return
	PyObject *ret_list = PyList_New(num_verts);
	if (!ret_list) {
		return NULL;
	}

	for (int i = 0; i < num_verts; i++) {

		// Create python tuple object
		PyObject *entry = Py_BuildValue("dd", vertices[i].x, vertices[i].y);
		if (!entry) {
			return NULL;
		}

		// Add the entry to the list; PyList_SET_ITEM doesn't do error checking
		// and "steals" a reference to entry. Meaning I don't have to decrease
		// entry's refcount. (Right?)
		// PyListSetItem will do error checking and will try to decrease the refcount
		// of whatever is being replaced, which in this case is NULL, so it would be
		// incorrect
		PyList_SET_ITEM(ret_list, i, entry);
	}

	return ret_list;
}

static PyObject *
config(PyObject *self, PyObject *args)
{
	double c1;
	double c2;
	double c3;
	double c4;
	bool threaded;
	int num_threads;

	if (!PyArg_ParseTuple(args, "ddddpi", &c1, &c2, &c3, &c4, &threaded, &num_threads)) {
		return NULL;
	}

	C1 = c1;
	C2 = c2;
	C3 = c3;
	C4 = c4;

	if (isnan(C1) || isnan(C2) || isnan(C3) || isnan(C4)) {
		fprintf(stderr, "NaN in config!\n"
				"C1: %f, C2: %f, C3 %f, C4: %f\n",
				C1, C2, C3, C4);
		exit(-1);
	}

	THREADED = threaded;
	NUM_THREADS = num_threads;

	Py_INCREF(Py_None);
	return Py_None;

}

static PyMethodDef FdagMethods[] = {
	{"fdag", fdag, METH_VARARGS, "Compute one iteration of the force-directed graph layout algorithm."},
	{"config", config, METH_VARARGS, "Set constants for computing the force-directed graphing algorithm."},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef fdagmodule = {
	PyModuleDef_HEAD_INIT,
	"fdag",
	NULL,
	-1,
	FdagMethods
};

PyMODINIT_FUNC
PyInit_fdag(void)
{
	return PyModule_Create(&fdagmodule);
}
